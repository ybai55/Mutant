import mutant
from mutant.server.fastapi import FastAPI

settings = mutant.config.Settings(mutant_db_impl="clickhouse",
                                  clickhouse_host="clickhouse",
                                  clickhouse_port="9000",)
server = FastAPI(settings)
app = server.app()
