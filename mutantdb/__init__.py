import mutantdb.config
import logging


__settings = mutantdb.config.Settings()


def configure(**kwargs):
    """Override Mutant's default settings, environment variables or .env files"""
    __settings = mutantdb.config.Settings(**kwargs)


def get_settings():
    return __settings


def get_db(settings=__settings):
    """Return a mutant.DB instance based on the provided or environmental settings."""

    setting = settings.mutant_db_impl.lower()

    def require(key):
        assert settings[key], f"Setting '{key}' is required when mutant_db_impl={setting}"

    if setting == "clickhouse":
        require("clickhouse_host")
        require("clickhouse_port")
        require("mutant_cache_dir")
        print("Using Clickhouse for database")
        import mutantdb.db.clickhouse

        return mutantdb.db.clickhouse.Clickhouse(settings)
    elif setting == "duckdb+parquet":
        require("mutant_cache_dir")
        import mutantdb.db.duckdb

        return mutantdb.db.duckdb.PersistentDuckDB(settings)
    elif setting == "duckdb":
        require("mutant_cache_dir")
        print("Using DuckDB in-memory for database. Data will be transient.")
        import mutantdb.db.duckdb

        return mutantdb.db.duckdb.DuckDB(settings)
    else:
        raise Exception(f"Unknown value '{setting} for mutant_db_impl")


def Client(settings=__settings):
    """Return a mutant.API instance based on the provided or environmental
    settings, optionally overriding the DB instance."""

    setting = settings.mutant_api_impl.lower()

    def require(key):
        assert settings[key], f"Setting '{key}' is required when mutant_api_impl={setting}"

    if setting == "arrowflight":
        require("mutant_server_host")
        require("mutant_server_grpc_port")
        print("Running Mutant in client mode using ArrowFlight to connect to remote server")
        import mutantdb.api.arrowflight

        return mutantdb.api.arrowflight.ArrowFlightAPI(settings)
    elif setting == "rest":
        require("mutant_server_host")
        require("mutant_server_http_port")
        print("Running Mutant in client mode using REST to connect to remote server")
        import mutantdb.api.fastapi

        return mutantdb.api.fastapi.FastAPI(settings)
    elif setting == "celery":
        require("celery_broker_url")
        require("celery_result_backend")
        print("Running Mutant in server mode with Celery jobs enabled.")
        import mutantdb.api.celery

        return mutantdb.api.celery.CeleryAPI(settings, get_db(settings))
    elif setting == "local":
        print("Running Mutant using direct local API.")
        import mutantdb.api.local

        return mutantdb.api.local.LocalAPI(settings, get_db(settings))
    else:
        raise Exception(f"Unknown value '{setting} for mutant_api_impl")
