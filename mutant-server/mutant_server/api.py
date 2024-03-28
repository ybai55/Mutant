import os
from random import sample
import shutil
import time
from typing import Callable

from fastapi import FastAPI, Response, status
from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute

from mutant_server.db.clickhouse import Clickhouse
from mutant_server.index.hnswlib import Hnswlib
from mutant_server.types import AddEmbedding, QueryEmbedding, ProcessEmbedding, FetchEmbedding, CountEmbedding, RawSql
from mutant_server.logger import logger

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
# that being said, we will only store a single string, "space_key" in the db, which the user can, in principle, override
# - embeddings are always written with and fetched from the same space_key
# - indexes are specific to a space_key and a timestamp
# - the client can handle the app + model_version + layer => space_key string generation

# API Endpoints


@app.get("/api/v1")
async def root():
    """
    Heartbeat endpoint
    """
    return {"nanosecond heartbeat": int(1000 * time.time_ns())}


@app.post("/api/v1/add", status_code=status.HTTP_201_CREATED)
async def add_to_db(new_embedding: AddEmbedding):
    """
    Save embedding to database
    - supports single or batched embeddings
    """
    # print("add_to_db, new_embedding.space_key", new_embedding, new_embedding.space_key)

    app._db.add_batch(
        new_embedding.space_key,
        new_embedding.embedding_data,
        new_embedding.input_uri,
        new_embedding.dataset,
        new_embedding.custom_quality_score,
        new_embedding.category_name,
    )

    return {"response": "Added record to database"}


@app.get("/api/v1/process")
async def process(process_embedding: ProcessEmbedding):
    """
    Currently generates an index for the embedding db
    """
    where_filter = {"space_key": process_embedding.space_key}
    # print("process, where_filter", where_filter)
    app._ann_index.run(process_embedding.space_key, app._db.fetch(where_filter))


@app.get("/api/v1/fetch")
async def fetch(fetch_embedding: FetchEmbedding):
    """
    Fetches embeddings from the database
    - enables filtering by where_filter, sorting by key, and limiting the number of results
    """
    return app._db.fetch(fetch_embedding.where_filter, fetch_embedding.sort, fetch_embedding.limit)


@app.get("/api/v1/count")
async def count(count_embedding: CountEmbedding):
    """
    Returns the number of records in the database
    """
    return {"count": app._db.count(space_key=count_embedding.space_key)}


@app.get("/api/v1/reset")
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
    if embedding.space_key is None:
        return {"error": "space_key is required"}

    ids = None

    filter_by_where = {}
    filter_by_where["space_key"] = embedding.space_key
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
        embedding.space_key, embedding.embedding, embedding.n_results, ids
    )
    print("uuids", uuids)
    print("distances", distances.tolist()[0])
    return {
        "ids": uuids,
        "embeddings": app._db.get_by_ids(uuids),
        "distances": distances.tolist()[0],
    }

@app.get("/api/v1/raw_sql")
async def raw_sql(raw_sql: RawSql):
    return app._db.raw_sql(raw_sql.raw_sql)
