"""
Tests de andi.webservice.dbpool
"""
import logging

import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
import andi.webservice.dbpool as target

app = FastAPI()
client = TestClient(app)

logger = logging.getLogger("testing")


@app.get("/")
async def some_route(db=Depends(target.get)):
    """
    Montre juste le connecteur de BD fourni par le pool
    """
    return db


async def fake_factory():
    class FakePool:
        def __init__(self):
            self._pool = [1, 2, 3]

        async def acquire(self):
            connection = self._pool.pop()
            logger.info(f"acquiring {connection}")
            return connection

        async def release(self, connection):
            logger.info(f"releasing {connection}")
            self._pool.insert(0, connection)

    return FakePool()


@pytest.fixture(scope="function")
async def faking_pool():
    return await target.init(fake_factory)


def test_manager_get(faking_pool, caplog):
    """
    Fonctionnement du manager de pool de connexions
    """
    caplog.set_level(logging.INFO, logger="testing")
    caplog.clear()
    response = client.get("/")
    assert response.json() == 3
    assert caplog.messages == ["acquiring 3", "releasing 3"]

    caplog.clear()
    response = client.get("/")
    assert response.json() == 2
    assert caplog.messages == ["acquiring 2", "releasing 2"]
