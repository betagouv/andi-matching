"""
Fixtures pour pytest
"""
import pathlib

import fastapi
import fastapi.testclient
import pytest
from andi.webservice.asgi import app as real_app


@pytest.fixture(scope="session", autouse=True)
def session_setup_teardown():
    # Setup
    yield
    # Teardown


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
