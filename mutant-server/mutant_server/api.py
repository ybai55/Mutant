import time

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from mutant_server.worker import heavy_offline_analysis

from mutant_server.db.clickhouse import Clickhouse
from mutant_server.index.hnswlib import Hnswlib
from mutant_server.types import (
    AddEmbedding,
    QueryEmbedding,
    ProcessEmbedding,
    FetchEmbedding,
    CountEmbedding,
    RawSql,
    Results,
    SpaceKeyInput,
    DeleteEmbedding
)
from mutant_server.utils.telemetry.capture import Capture
from mutant_server.utils.error_reporting import init_error_reporting

mutant_telemetry = Capture()
mutant_telemetry.capture('server-start')
init_error_reporting()

from celery.result import AsyncResult

# Boot script
db = Clickhouse
ann_index = Hnswlib

app = FastAPI(debug=True)

# init db and index
app._db = db()
app._ann_index = ann_index()


# scoping
# an embedding space is specific to particular trained model and layer
# instead of making the user manage this complexity, we will handle some conventions here
# that being said, we will only store a single string, "model_space" in the db, which the user can, in principle, override
# - embeddings are always written with and fetched from the same model_space
# - indexes are specific to a model_space and a timestamp
# - the client can handle the app + model_version + layer => model_space string generation

# API Endpoints


@app.get("/api/v1")
async def root():
    """
    Heartbeat endpoint
    """
    return {"nanosecond heartbeat": int(1000 * time.time_ns())}


@app.post("/api/v1/calculate_results")
async def calculate_results(model_space: SpaceKeyInput):
    task = heavy_offline_analysis(model_space)
    mutant_telemetry.capture('heavy-offline-analysis')
    return JSONResponse({"task_id": task.id})


@app.post("/api/v1/tasks/{task_id}")
async def get_status(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result,
    }
    return JSONResponse(result)


@app.post("/api/v1/get_results")
async def get_results(results: Results):
    return app._db.return_results(results.model_space, results.n_results)


@app.post("/api/v1/add", status_code=status.HTTP_201_CREATED)
async def add(new_embedding: AddEmbedding):
    """
    Save embedding to database
    - supports single or batched embeddings
    """
    # print("add_to_db, new_embedding.model_space", new_embedding, new_embedding.model_space)
    number_of_embeddings = len(new_embedding.embedding_data)

    if isinstance(new_embedding.model_space, str):
        model_space = [new_embedding.model_space] * number_of_embeddings
    elif len(new_embedding.model_space) == 1:
        model_space = [new_embedding.model_space[0]] * number_of_embeddings
    else:
        model_space = new_embedding.model_space

    if isinstance(new_embedding.dataset, str):
        dataset = [new_embedding.dataset] * number_of_embeddings
    elif len(new_embedding.dataset) == 1:
        dataset = [new_embedding.dataset[0]] * number_of_embeddings
    else:
        dataset = new_embedding.dataset

    # print the len of all inputs to add
    print(len(new_embedding.embedding_data), len(new_embedding.input_uri), len(model_space), len(dataset))

    app._db.add(
        model_space,
        new_embedding.embedding_data,
        new_embedding.input_uri,
        dataset,
        None,
        new_embedding.category_name,
    )

    return {"response": "Added record to database"}


@app.post("/api/v1/process")
async def process(process_embedding: ProcessEmbedding):
    """
    Currently generates an index for the embedding db
    """
    fetch = app._db.fetch({"model_space": process_embedding.model_space}, columnar=True)
    # print("process, where_filter", where_filter)
    mutant_telemetry.capture('capture-index', {'n', len(fetch[2])})
    app._ann_index.run(process_embedding.model_space, fetch[1], fetch[2])  # more magic number, ugh

    return {"response": "Processed space"}


@app.post("/api/v1/fetch")
async def fetch(embedding: FetchEmbedding):
    """
    Fetches embeddings from the database
    - enables filtering by where_filter, sorting by key, and limiting the number of results
    """
    return app._db.fetch(embedding.where_filter, embedding.sort, embedding.limit, embedding.offset)


@app.post("/api/v1/delete")
async def delete(embedding: DeleteEmbedding):
    """
    Deletes embeddings from the database
    - enables filtering by where_filter
    """
    return app._db.delete(embedding.where_filter)


@app.get("/api/v1/count")
async def count(model_space: str = None):
    """
    Returns the number of records in the database
    """
    return {"count": app._db.count(model_space=model_space)}


@app.post("/api/v1/reset")
async def reset():
    """
    Reset the database and index
    """
    app._db = db()
    app._db.reset()
    app._ann_index = ann_index()
    return True


@app.post("/api/v1/get_nearest_neighbors")
async def get_nearest_neighbors(embedding: QueryEmbedding):
    """
    return the distance, database ids, and embedding themselves for the input embedding
    """
    if embedding.model_space is None:
        return {"error": "model_space is required"}

    ids = None

    filter_by_where = {}
    filter_by_where["model_space"] = embedding.model_space
    if embedding.category_name is not None:
        filter_by_where["category_name"] = embedding.category_name
    if embedding.dataset is not None:
        filter_by_where["dataset"] = embedding.dataset

    if filter_by_where is not None:
        # print("app._db.fetch(filter_by_where)[uuid]")
        results = app._db.fetch(filter_by_where)
        # get the first element of each item in results
        ids = [str(item[1]) for item in results]  # 1 is the uuid column
        # ids = app._db.fetch(filter_by_where)["uuid"].tolist()

    # nn = app._ann_index.get_nearest_neighbors(embedding.embedding, embedding.n_results, ids)
    uuids, distances = app._ann_index.get_nearest_neighbors(
        embedding.model_space, embedding.embedding, embedding.n_results, ids
    )
    print("uuids", uuids)
    print("distances", distances.tolist()[0])
    return {
        "ids": uuids,
        "embeddings": app._db.get_by_ids(uuids),
        "distances": distances.tolist()[0],
    }


@app.post("/api/v1/raw_sql")
async def raw_sql(raw_sql: RawSql):
    return app._db.raw_sql(raw_sql.raw_sql)
