"""
Helper functions for the async database pool.
Avoids the use of globals.
"""
import logging
from typing import Callable, Any, Awaitable, AsyncGenerator

logger = logging.getLogger(__name__)

FactoryType = Callable[[], Awaitable[Any]]


async def init(factory: FactoryType):
    """
    Initialisation du manager
    Args:
        factory: Async function with no parameter that returns a db pool
    """
    await manager.init(factory)


async def get() -> AsyncGenerator[Any, None]:
    """
    Provides arbitrary free connection from the pool

    Yields:
        A DB connection from the pool
    """
    # Could have used generator within generator, but that
    # would have hampered code lisibility and comprehensibility
    # Besides, the DbPool class manages the pool, not the connections.
    pool = manager.get_pool()
    conn = await pool.acquire()
    try:
        yield conn
    finally:
        await pool.release(conn)


class InitialPool:
    """
    Un faux pool qui permet de faire sauter l'utilisation d'un manager non initialisé
    """

    async def acquire(self):
        raise RuntimeError("Using a PoolManager instance before running 'init(...)' method")

    async def release(self, conn: Any):
        raise RuntimeError("Using a PoolManager instance before running 'init(...)' method")


class PoolManager:
    def __init__(self):
        self._pool = InitialPool()

    async def init(self, pool_factory: FactoryType) -> None:
        self._pool = await pool_factory()
        logger.debug('Database pool initiated')

    def get_pool(self):
        return self._pool


# DBPool object accessor
manager = PoolManager()


async def tests_pool_factory():
    class TestsPool:
        def __init__(self):
            self._pool = [1, 2, 3]

        async def acquire(self):
            connection = self._pool.pop()
            logger.info(f"acquiring {connection}")
            return connection

        async def release(self, connection):
            logger.info(f"releasing {connection}")
            self._pool.insert(0, connection)

    return TestsPool()
