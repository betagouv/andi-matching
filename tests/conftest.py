"""
Fixtures pour pytest
"""
import json
import os
import pathlib
import sys

if sys.version_info >= (3, 8):
    pass
else:
    # Backport de unittest.mock de Python 3.8
    pass

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


@pytest.fixture(scope="session")
def mocked_aiohttp_response():
    class MockedResponse:
        """
        Une fausse réponse pour aiohttp.ClientSession.get
        Voir tests/test_conftest.py pour un exemple
        """

        def __init__(self, text, status):
            self._text = text
            self.status = status

        async def text(self):
            return self._text

        async def json(self):
            return json.loads(self._text)

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    return MockedResponse


skip_connected = pytest.mark.skipif(
    not os.getenv("AN4_RUN_CONNECTED_TESTS", "false") == "true",
    reason="Tests avec connexion non exécuté"
)
