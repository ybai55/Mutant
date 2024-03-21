from mutant_client import Mutant
import pytest
import time
from httpx import AsyncClient


@pytest.fixture
def anyio_backend():
    return 'asyncio'

def test_init():
    mutant = Mutant()
    assert mutant._api_url == 'http://localhost:8000/api/v1'