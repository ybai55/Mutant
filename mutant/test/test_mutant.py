import pytest
import unittest
from unittest.mock import patch

import mutant
import mutant.config


class GetDBTest(unittest.TestCase):

    @patch("mutant.db.duckdb.DuckDB", autospec=True)
    def test_default_db(self, mock):
        db = mutant.get_db(mutant.config.Settings(mutant_cache_dir="./foo"))
        assert mock.called

    @patch("mutant.db.duckdb.PersistentDuckDB", autospec=True)
    def test_persistent_duckdb(self, mock):
        db = mutant.get_db(mutant.config.Settings(mutant_db_impl="duckdb+parquet",
                                                  mutant_cache_dir="./foo"))
        assert mock.called

    @patch("mutant.db.clickhouse.Clickhouse", autospec=True)
    def test_clickhouse(self, mock):
        db = mutant.get_db(mutant.config.Settings(mutant_db_impl="clickhouse",
                                                  mutant_cache_dir="./foo",
                                                  clickhouse_host="foo",
                                                  clickhouse_port=666))
        assert mock.called


class GetAPITest(unittest.TestCase):

    @patch("mutant.db.duckdb.DuckDB", autospec=True)
    @patch("mutant.api.local.LocalAPI", autospec=True)
    def test_local(self, mock_api, mock_db):
        api = mutant.get_api(mutant.config.Settings(mutant_cache_dir="./foo"))
        assert mock_api.called
        assert mock_db.called

    @patch("mutant.db.duckdb.DuckDB", autospec=True)
    @patch("mutant.api.celery.CeleryAPI", autospec=True)
    def test_celery(self, mock_api, mock_db):
        api = mutant.get_api(mutant.config.Settings(mutant_api_impl="celery",
                                                    mutant_cache_dir="./foo",
                                                    celery_broker_url="foo",
                                                    celery_result_backend="foo"))
        assert mock_api.called
        assert mock_db.called

    @patch("mutant.api.fastapi.FastAPI", autospec=True)
    def test_fastapi(self, mock):
        api = mutant.get_api(
            mutant.config.Settings(mutant_api_impl="rest",
                                   mutant_cache_dir="./foo",
                                   mutant_server_host="foo",
                                   mutant_server_http_port="80")
        )
        assert mock.called

    @patch("mutant.api.arrowflight.ArrowFlightAPI", autospec=True)
    def test_arrowflight(self, mock):
        api = mutant.get_api(
            mutant.config.Settings(mutant_api_impl="arrowflight",
                                   mutant_cache_dir="./foo",
                                   mutant_server_host="foo",
                                   mutant_server_grpc_port="9999"))
        assert mock.called