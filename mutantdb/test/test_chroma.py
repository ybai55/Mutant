import unittest
import os
from unittest.mock import patch, Mock
import pytest
import mutantdb
import mutantdb.config
from mutantdb.db.system import SysDB
from mutantdb.ingest import Consumer, Producer


class GetDBTest(unittest.TestCase):
    @patch("mutantdb.db.impl.sqlite.SqliteDB", autospec=True)
    def test_default_db(self, mock: Mock) -> None:
        system = mutantdb.config.System(
            mutantdb.config.Settings(persist_directory="./foo")
        )
        system.instance(SysDB)
        assert mock.called

    @patch("mutantdb.db.impl.sqlite.SqliteDB", autospec=True)
    def test_sqlite_sysdb(self, mock: Mock) -> None:
        system = mutantdb.config.System(
            mutantdb.config.Settings(
                mutant_sysdb_impl="mutantdb.db.impl.sqlite.SqliteDB",
                persist_directory="./foo",
            )
        )
        system.instance(SysDB)
        assert mock.called

    @patch("mutantdb.db.impl.sqlite.SqliteDB", autospec=True)
    def test_sqlite_queue(self, mock: Mock) -> None:
        system = mutantdb.config.System(
            mutantdb.config.Settings(
                mutant_sysdb_impl="mutantdb.db.impl.sqlite.SqliteDB",
                mutant_producer_impl="mutantdb.db.impl.sqlite.SqliteDB",
                mutant_consumer_impl="mutantdb.db.impl.sqlite.SqliteDB",
                persist_directory="./foo",
            )
        )
        system.instance(Producer)
        system.instance(Consumer)
        assert mock.called


class GetAPITest(unittest.TestCase):
    @patch("mutantdb.api.segment.SegmentAPI", autospec=True)
    @patch.dict(os.environ, {}, clear=True)
    def test_local(self, mock_api: Mock) -> None:
        mutantdb.Client(mutantdb.config.Settings(persist_directory="./foo"))
        assert mock_api.called

    @patch("mutantdb.db.impl.sqlite.SqliteDB", autospec=True)
    @patch.dict(os.environ, {}, clear=True)
    def test_local_db(self, mock_db: Mock) -> None:
        mutantdb.Client(mutantdb.config.Settings(persist_directory="./foo"))
        assert mock_db.called

    @patch("mutantdb.api.fastapi.FastAPI", autospec=True)
    @patch.dict(os.environ, {}, clear=True)
    def test_fastapi(self, mock: Mock) -> None:
        mutantdb.Client(
            mutantdb.config.Settings(
                mutant_api_impl="mutantdb.api.fastapi.FastAPI",
                persist_directory="./foo",
                mutant_server_host="foo",
                mutant_server_http_port="80",
            )
        )
        assert mock.called

    @patch("mutantdb.api.fastapi.FastAPI", autospec=True)
    @patch.dict(os.environ, {}, clear=True)
    def test_settings_pass_to_fastapi(self, mock: Mock) -> None:
        settings = mutantdb.config.Settings(
            mutant_api_impl="mutantdb.api.fastapi.FastAPI",
            mutant_server_host="foo",
            mutant_server_http_port="80",
            mutant_server_headers={"foo": "bar"},
        )
        mutantdb.Client(settings)

        # Check that the mock was called
        assert mock.called

        # Retrieve the arguments with which the mock was called
        # `call_args` returns a tuple, where the first element is a tuple of positional arguments
        # and the second element is a dictionary of keyword arguments. We assume here that
        # the settings object is passed as a positional argument.
        args, kwargs = mock.call_args
        passed_settings = args[0] if args else None

        # Check if the settings passed to the mock match the settings we used
        # raise Exception(passed_settings.settings)
        assert passed_settings.settings == settings


def test_legacy_values() -> None:
    with pytest.raises(ValueError):
        mutantdb.Client(
            mutantdb.config.Settings(
                mutant_api_impl="mutantdb.api.local.LocalAPI",
                persist_directory="./foo",
                mutant_server_host="foo",
                mutant_server_http_port="80",
            )
        )
