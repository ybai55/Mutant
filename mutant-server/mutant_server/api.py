import time
import os


from mutant_server.db.clickhouse import Clickhouse
from mutant_server.db.duckdb import DuckDB
from mutant_server.index.hnswlib import Hnswlib
from mutant_server.utils.error_reporting import init_error_reporting
from mutant_server.utils.telemetry.capture import Capture
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

mutant_telemetry = Capture()
mutant_telemetry.capture("server-start")
init_error_reporting()

from mutant_server.routes import MutantRouter

# current valid modes are 'in-memory' and 'docker', it defaults to docker
mutant_mode = os.getenv("MUTANT_MODE", "docker")
if mutant_mode == "in-memory":
    db = DuckDB
else:
    db = Clickhouse

ann_index = Hnswlib

app = FastAPI(debug=True)

# Boot script
app._db = db()
app._ann_index = ann_index


def create_index_data_dir():
    if not os.path.exists(os.getcwd() + "/index_data"):
        os.makedirs(os.getcwd() + '/index_data')
    app._ann_index.set_save_folder(os.getcwd() + '/index_data')

if mutant_mode == 'in-memory':
    create_index_data_dir()

router = MutantRouter(app=app, db=db(), ann_index=ann_index())
app.include_router(router.router)

# enables CORS
app.add_middleware(
    CORSMiddleware,
    allow_headers=["*"],
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
)

