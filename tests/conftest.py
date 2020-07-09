"""
Fixtures pour pytest
"""
import pathlib

import pytest


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
