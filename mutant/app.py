import mutant
from mutant.server.fastapi import FastAPI

server = FastAPI(mutant.get_settings())
app = server.app()
