import mutant
from mutant.config import Settings
import mutant.server.fastapi
import pytest
import time
import tempfile
import copy
from multiprocessing import Process
import uvicorn
from requests.exceptions import ConnectionError


@pytest.fixture
def local_api():
    return mutant.get_api(
        mutant.config.Settings(
            mutant_api_impl="local", mutant_db_impl="duckdb", mutant_cache_dir=tempfile.gettempdir()
        )
    )


def _build_fastapi_api():
    return mutant.get_api(
        Settings(
            mutant_api_impl="rest", mutant_server_host="localhost", mutant_server_http_port="8888"
        )
    )


@pytest.fixture
def fastapi_api():
    return _build_fastapi_api()


def run_server():
    settings = Settings(
        mutant_api_impl="local",
        mutant_db_impl="duckdb",
        mutant_cache_dir=tempfile.gettempdir() + "/test_server",
    )
    server = mutant.server.fastapi.FastAPI(settings)
    uvicorn.run(server.app(), host="0.0.0.0", port=8888, log_level="info")


def await_server(attempts=0):
    api = _build_fastapi_api()

    try:
        api.heartbeat()
    except ConnectionError as e:
        if attempts > 10:
            raise e
        else:
            time.sleep(2)
            await_server(attempts + 1)


@pytest.fixture(scope="module", autouse=True)
def fastapi_server():
    proc = Process(target=run_server, args=(), daemon=True)
    proc.start()
    await_server()
    yield
    proc.kill()


test_apis = [local_api, fastapi_api]


@pytest.mark.parametrize("api_fixture", test_apis)
def test_heartbeat(api_fixture, request):
    api = request.getfixturevalue(api_fixture.__name__)

    assert isinstance(api.heartbeat(), int)


batch_records = {
    "embedding": [[1.1, 2.3, 3.2], [1.2, 2.24, 3.2]],
    "input_uri": ["https://example.com", "https://example.com"],
    "dataset": ["training", "training"],
    "inference_class": ["knife", "person"],
    "model_space": ["test_space", "test_space"],
    "label_class": ["person", "person"],
}


@pytest.mark.parametrize("api_fixture", test_apis)
def test_add(api_fixture, request):
    api = request.getfixturevalue(api_fixture.__name__)

    api.reset()

    api.add(**batch_records)

    assert api.count(model_space="test_space") == 2


@pytest.mark.parametrize("api_fixture", test_apis)
def test_add_with_default_model_space(api_fixture, request):
    api = request.getfixturevalue(api_fixture.__name__)

    api.reset()

    api.set_model_space("foobar")

    records = copy.deepcopy(batch_records)
    records["model_space"] = None
    api.add(**records)

    assert api.count() == 2
    assert api.count(model_space="foobar") == 2


minimal_records = {
    "embedding": [[1.1, 2.3, 3.2], [1.2, 2.24, 3.2]],
    "input_uri": ["https://example.com", "https://example.com"],
    "dataset": "training",
    "inference_class": ["person", "person"],
    "model_space": "test_space",
}


@pytest.mark.parametrize("api_fixture", test_apis)
def test_add_minimal(api_fixture, request):
    api = request.getfixturevalue(api_fixture.__name__)

    api.reset()

    api.add(**minimal_records)

    assert api.count(model_space="test_space") == 2


@pytest.mark.parametrize("api_fixture", test_apis)
def test_fetch_from_db(api_fixture, request):
    api = request.getfixturevalue(api_fixture.__name__)

    api.reset()
    api.add(**batch_records)
    records = api.fetch(where={"model_space": "test_space"})

    assert len(records["embedding"]) == 2


@pytest.mark.parametrize("api_fixture", test_apis)
def test_reset_db(api_fixture, request):
    api = request.getfixturevalue(api_fixture.__name__)

    api.reset()

    api.add(**batch_records)
    assert api.count(model_space="test_space") == 2

    assert api.reset()
    assert api.count(model_space="test_space") == 0


@pytest.mark.parametrize("api_fixture", test_apis)
def test_get_nearest_neighbors(api_fixture, request):
    api = request.getfixturevalue(api_fixture.__name__)

    api.reset()
    api.add(**batch_records)
    assert api.create_index(model_space="test_space")

    nn = api.get_nearest_neighbors(
        embedding=[1.1, 2.3, 3.2], n_results=1, where={"model_space": "test_space"}
    )

    assert len(nn["ids"]) == 1


@pytest.mark.parametrize("api_fixture", test_apis)
def test_get_nearest_neighbors_filter(api_fixture, request):
    api = request.getfixturevalue(api_fixture.__name__)

    api.reset()
    api.add(**minimal_records)
    assert api.create_index(model_space="test_space")

    with pytest.raises(Exception) as e:
        nn = api.get_nearest_neighbors(
            embedding=[1.1, 2.3, 3.2],
            n_results=1,
            where={"model_space": "test_space", "inference_class": "monkey", "dataset": "training"},
        )

    assert str(e.value).__contains__("found")


@pytest.mark.parametrize("api_fixture", test_apis)
def test_delete(api_fixture, request):
    api = request.getfixturevalue(api_fixture.__name__)

    api.reset()
    api.set_model_space("test_space")
    api.add(**batch_records)
    assert api.count() == 2
    assert api.delete(where={"model_space": "foobar"}) == []
    assert api.count() == 2
    assert api.delete()
    assert api.count() == 0


@pytest.mark.parametrize("api_fixture", test_apis)
def test_delete_with_index(api_fixture, request):
    api = request.getfixturevalue(api_fixture.__name__)

    api.reset()
    api.set_model_space("test_space")
    api.add(**batch_records)
    assert api.count() == 2
    api.create_index()
    nn = api.get_nearest_neighbors(embedding=[1.1, 2.3, 3.2],
                                   n_results=1)

    assert nn['embeddings']['inference_class'][0] == 'knife'

    assert api.delete(where={"inference_class": "knife"})

    nn2 = api.get_nearest_neighbors(embedding=[1.1, 2.3, 3.2],
                                    n_results=1)
    assert nn2['embeddings']['inference_class'][0] == 'person'

