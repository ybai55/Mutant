import pytest
import unittest
import os
from unittest.mock import patch

import mutantdb
import mutantdb.config

class GetDBTest(unittest.TestCase):

    @patch('mutantdb.db.duckdb.DuckDB', autospec=True)
    def test_default_db(self, mock):
        db = mutantdb.get_db(mutantdb.config.Settings(persist_directory="./foo"))
        assert mock.called


    @patch('mutantdb.db.duckdb.PersistentDuckDB', autospec=True)
    def test_persistent_duckdb(self, mock):
        db = mutantdb.get_db(mutantdb.config.Settings(mutant_db_impl="duckdb+parquet",
                                                  persist_directory="./foo"))
        assert mock.called


    @patch('mutantdb.db.clickhouse.Clickhouse', autospec=True)
    def test_clickhouse(self, mock):
        db = mutantdb.get_db(mutantdb.config.Settings(mutant_db_impl="clickhouse",
                                                  persist_directory="./foo",
                                                  clickhouse_host="foo",
                                                  clickhouse_port=666))
        assert mock.called

class GetAPITest(unittest.TestCase):

    @patch('mutantdb.db.duckdb.DuckDB', autospec=True)
    @patch('mutantdb.api.local.LocalAPI', autospec=True)
    @patch.dict(os.environ, {}, clear=True)
    def test_local(self, mock_api, mock_db):
        api = mutantdb.Client(mutantdb.config.Settings(persist_directory="./foo"))
        assert mock_api.called
        assert mock_db.called



    @patch('mutantdb.api.fastapi.FastAPI', autospec=True)
    @patch.dict(os.environ, {}, clear=True)
    def test_fastapi(self, mock):
        api = mutantdb.Client(mutantdb.config.Settings(mutant_api_impl="rest",
                                                    persist_directory="./foo",
                                                    mutant_server_host='foo',
                                                    mutant_server_http_port='80'))
        assert mock.called
