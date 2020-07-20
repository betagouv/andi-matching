"""
Initialise et fournit l'objet app pour un moteur ASGI (uvicorn, ...)
"""
import os

import asyncpg
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from . import settings, romesuggest, dbpool, __version__
from .routers import all_routers


def create_asgi_app() -> FastAPI:
    """
    Factory d'appli ASGI

    Returns:
        Application ASGI andi-matching initialisée et paramétrée
    """
    # On bootstrape la config si nécessaire
    config = settings.config

    # Juste pour bootstrapper l'index Whoosh
    _ = romesuggest.SUGGEST_STATE

    # Construction et paramétrage de l'app ASGI
    app = FastAPI(
        title="ANDi API",
        description="Documentation et tests des différents points d'accès de l'API ANDi.",
        version=__version__,
        **config.FASTAPI_OPTIONS)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def startup_event():
        # Do not initiate DB Pool when testing (AN4_NO_DB_CONNECTION is a test-environment specific variable)
        async def pool_factory():
            pool = await asyncpg.create_pool(**config.PG_CONNECTIONS_POOL)
            return pool

        if os.getenv('AN4_NO_DB_CONNECTION', 'false') == 'false':
            await dbpool.init(pool_factory)

    for router in all_routers:
        app.include_router(router)
    return app


app = create_asgi_app()
