import asyncpg
import logging

logger = logging.getLogger(__name__)


async def init(config):
    await db_pool.init(config)


async def get():
    pool = db_pool.get_pool()
    conn = await pool.acquire()
    try:
        yield conn
    finally:
        await pool.release(conn)


class DbPool:
    _pool = False

    def __init__(self):
        self._pool = []

    async def init(self, config):
        self._pool = await asyncpg.create_pool(**config['postgresql'])
        logger.debug('Database pool initiated')

    def get_pool(self):
        return self._pool


# ## Init DBPool object accessor
db_pool = DbPool()
