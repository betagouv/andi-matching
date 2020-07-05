"""
Fixtures pour pytest
"""
import pathlib

import pytest


@pytest.fixture(scope="session")
def data_directory():
    return pathlib.Path(__file__).resolve().parent / "data"
