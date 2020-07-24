"""
Fixtures pour pytest
"""
import os
import pathlib
import sys

if sys.version_info >= (3, 8):
    import unittest.mock as mock
else:
    # Backport de unittest.mock de Python 3.8
    import mock

import fastapi
import fastapi.testclient
import pytest
from andi.webservice.asgi import app as real_app


@pytest.fixture(scope="session", autouse=True)
def session_setup_teardown():
    # Setup global
    yield
    # Teardown global


@pytest.fixture(scope="session")
def data_directory() -> pathlib.Path:
    """
    Returns:
        Le répertoire des données de tests
    """
    return pathlib.Path(__file__).resolve().parent / "data"


@pytest.fixture(scope="session")
def source_tree() -> pathlib.Path:
    """
    Returns:
        Le répertoire racine du répôt local
    """
    return pathlib.Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def app() -> fastapi.FastAPI:
    return real_app


@pytest.fixture(scope="session")
def client(app) -> fastapi.testclient.TestClient:
    return fastapi.testclient.TestClient(app)


# Mocks pour aiohttp.ClientSession
# ================================

@pytest.fixture()
def mocked_aiohttp_get():
    async_mock = mock.AsyncMock()
    mock.patch("aiohttp.ClientSession.get.__aenter__", side_effect=async_mock)
    return async_mock


@pytest.fixture(scope="session")
def mocked_aiohttp_response():
    class MockedResponse:
        """
        Une fausse réponse pour aiohttp.ClientSession.get
        """

        def __init__(self, data):
            self._data = data

        async def json(self):
            return self._data

    return MockedResponse


skip_connected = pytest.mark.skipif(
    not os.getenv("AN4_RUN_CONNECTED_TESTS", "false") == "true",
    reason="Tests avec connexion non exécuté"
)
