import mutant
from mutant.server.fastapi import FastAPI

settings = mutant.config.Settings()
server = FastAPI(settings)
app = server.app()
