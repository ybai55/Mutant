import pytest
import time
from httpx import AsyncClient

from ..api import app


@pytest.mark.anyio
async def test_root():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        response = await ac.get("/api/v1")
    assert response.status_code == 200
    assert (abs(response.json()["nanosecond heartbeat"] - int(1000 * time.time_ns()))
            < 1_000_000_000)  # a billion nanoseconds


async def post_one_record(ac):
    return await ac.post("/api/v1/add",  json={
        "embedding_data": [1.02, 2.03, 3.03],
        "meta_data": {},
        "input_uri": "https://example.com",
        "inference_data": {"test": "Test"},
        "app": "yolov3",
        "model_version": "1.0.0",
        "layer": "pool5",
        "dataset": "coco",
    })


@pytest.mark.anyio
async def post_batch_records(ac):
    return await ac.post("/api/v1/add", json={
        "embedding_data": [[1.1, 2.3, 3.2], [1.2, 2.24, 3.2]],
        "meta_data": [{"test": "Test"}, {"test": "Test"}],
        "input_uri": ["https://example.com", "https://example.com"],
        "inference_data": [{"test": "Test"}, {"test": "Test"}],
        "app": ["yolov3", "yolov3"],
        "model_version": ["1.0.0", "1.0.0"],
        "layer": ["pool5", "pool5"],
        "dataset": "training",
    })


@pytest.mark.anyio
async def test_add_to_db():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        response = await post_one_record(ac)
    assert response.status_code == 201
    assert response.json() == {"response": "Added record to database"}


@pytest.mark.anyio
async def test_add_to_db_batch():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        response = await post_batch_records(ac)
    assert response.status_code == 201
    assert response.json() == {"response": "Added record to databse"}


@pytest.mark.anyio
async def test_fetch_from_db():
    async with AsyncClient(app=app, base_url='http://test') as ac:
        await post_one_record(ac)
        response = await ac.get("/api/v1/fetch", params={"limit": 1})
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.anyio
async def test_count_from_db():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.get("/api/v1/reset") # reset db
        await post_batch_records(ac)
        response = await ac.get("/api/v1/count")
    assert response.status_code == 200
    assert response.json() == {"count": 2}


@pytest.mark.anyio
async def test_reset_db():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.get("/api/v1/reset")
        await post_batch_records(ac)
        response = await ac.get("/api/v1/count")
        assert response.json() == {"count": 2}
        response = await ac.get("/api/v1/reset")
        assert response.json() == True
        response = await ac.get("/api/v1/count")
        assert response.json() == {"count": 0}


