import mutantdb
from mutantdb.server.fastapi import FastAPI

settings = mutantdb.config.Settings()
server = FastAPI(settings)
app = server.app()
