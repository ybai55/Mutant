import mutant.config

__settings = mutant.config.Settings()


def configure(**kwargs):
    """Override Mutant's default settings, environment variables or .env files"""
    __settings = mutant.config.Settings(**kwargs)


def get_settings():
    return __settings


def get_db(settings=__settings):
    """Return a mutant.DB instance based on the provided or environmental settings."""

    if settings.clickhouse_host:
        print("Using Clickhouse for database")
        import mutant.db.clickhouse

        return mutant.db.clickhouse.Clickhouse(settings)
    elif settings.mutant_cache_dir:
        print("Using DuckDB with local filesystem persistence for database")
        import mutant.db.duckdb

        return mutant.db.duckdb.PersistentDuckDB(settings)
    else:
        print("Using DuckDB in-memory for database. Data will be transient.")
        import mutant.db.duckdb

        return mutant.db.duckdb.DuckDB(settings)


def get_api(settings=__settings):
    """Return a mutant. API instance based on the provided or environmental
    settings, optionally overriding the DB instance."""

    if settings.mutant_server_host and settings.mutant_server_grpc_port:
        print("Running mutant in client/server mode using ArrowFlight protocol.")
        import mutant.api.arrowflight

        return mutant.api.arrowflight.ArrowFlightAPI(settings)
    elif settings.mutant_server_host and settings.mutant_server_http_port:
        print("Running mutant in client/server mode using REST protocol.")
        import mutant.api.fastapi

        return mutant.api.fastapi.FastAPI(settings)
    elif settings.celery_broker_url:
        print("Running mutant in server mode with Celery jobs enabled.")
        import mutant.api.celery

        return mutant.api.celery.CeleryAPI(settings, get_db(settings))
    else:
        print("Running mutant using direct local API.")
        import mutant.api.local

        return mutant.api.local.LocalAPI(settings, get_db(settings))
