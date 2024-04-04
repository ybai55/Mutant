import os
from fastapi import FastAPI

from mutant_server.routes import MutantRouter
from mutant_server.index.hnswlib import Hnswlib
from mutant_server.db.duckdb import DuckDB

# we import types here so that the user can import them from here
from mutant_server.types import (ProcessEmbedding, AddEmbedding, FetchEmbedding, QueryEmbedding,
                                 CountEmbedding, DeleteEmbedding, RawSql, Results, SpaceKeyInput)


core = FastAPI(debug=True)
core._db = DuckDB()
core._ann_index = Hnswlib()

router = MutantRouter(app=core, db=DuckDB, ann_index=Hnswlib)
core.include_router(router.router)

def init(filesystem_location: str = None):
    if filesystem_location is None:
        filesystem_location = os.getcwd()

    # create a dir
    if not os.path.exists(filesystem_location + '/.mutant'):
        os.makedirs(filesystem_location + '/.mutant')

    if not os.path.exists(filesystem_location + '/.mutant/index_data'):
        os.makedirs(filesystem_location + '/.mutant/index_data')

    # specify where to save and load data from
    core._db.set_save_folder(filesystem_location + '/.mutant')

# headless mode
core.heartbeat = router.root
core.add = router.add
core.count = router.count
core.fetch = router.fetch
core.reset = router.reset
core.delete = router.delete
core.get_nearest_neighbors = router.get_nearest_neighbors
core.raw_sql = router.raw_sql
core.create_index = router.create_index

# these as currently constructed require celery
# mutant_core.process = process
# core.get_status = get_status
# core.get_results = get_results
