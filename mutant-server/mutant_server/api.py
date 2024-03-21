import os
import shutil
import time

from fastapi import FastAPI, Response, status

from mutant_server.db.duckdb import DuckDB
from mutant_server.index.hnswlib import Hnswlib
from mutant_server.algorithms.rand_subsample import rand_bisectional_subsample
from mutant_server.types import AddEmbedding
from mutant_server.utils import logger


# Boot script
db = DuckDB
ann_index = Hnswlib
base_metadata = {
    "app": "yolov3",
    "model_version": "1.0.0",
    "layer": "pool5",
}

app = FastAPI(debug=True)

# init db and index
app._db = db()
app._ann_index = ann_index()

if not os.path.exists(".mutant"):
    os.mkdir(".mutant")

if os.path.exists(".mutant/mutant.parquet"):
    logger.info("Loading existing mutant database")
    app._db.load()

if os.path.exists(".mutant/index.bin"):
    logger.info("Loading existing mutant index")
    app._ann_index.load(app._db.count(), len(app._db.fetch(limit=1).embedding_data))


# API Endpoints
@app.get("/api/v1")
async def root():
    """
    Heartbeat endpoint
    """
    return {"nanosecond heartbeat": int(1000 * time.time_ns())}

@app.get("/api/v1/add", status_code=status.HTTP_201_CREATED)
async def add_to_db(new_embedding: AddEmbedding):
    """
    Save embedding to database
    - supports single or batched embeddings
    """
    app._db.add_batch(
        new_embedding.embedding_data,
        new_embedding.metadata,
        new_embedding.input_uri,
        new_embedding.inference_data,
        new_embedding.app,
        new_embedding.model_version,
        new_embedding.layer,
        new_embedding.dataset,
        new_embedding.distance,
        new_embedding.category_name
    )

    return {"response": "Added record to database"}


@app.get("/api/v1/process")
async def process(metadata={}):
    """
    Currently generates an index for the embedding db
    """
    app._ann_index.run(app._db.fetch())


@app.get("/api/v1/fetch")
async def fetch(metadata={}, sort=None, limit=None):
    """
    Fetches embeddings from the database
    - enables filtering by metadata, sorting by key, and limiting the number of results
    """
    return app._db.fetch(metadata, sort, limit).to_dict(orient="records")


@app.get("/api/v1/count")
async def count():
    """
    Returns the number of records in the database
    """
    return ({"count": app._db.count()})


@app.get("/api/v1/persist")
async def persist():
    '''
    Persist the database and index to disk
    '''
    if not os.path.exists(".mutant"):
        os.mkdir(".mutant")

    app._db.persist()
    app._ann_index.persist()
    return True


@app.get("/api/v1/reset")
async def reset():
    '''
    Reset the database and index
    '''
    shutil.rmtree(".mutant", ignore_errors=True)
    app._db = db()
    app._ann_index = ann_index()
    return True


@app.get("/api/v1/rand")
async def rand(metadata={}, sort=None, limit=None):
    '''
    Randomly bisection the database
    '''
    results = app._db.fetch(metadata, sort, limit)
    rand = rand_bisectional_subsample(results)
    return rand.to_dict(orient="records")