"""
Initialise et fournit l'objet app pour un moteur ASGI (uvicorn, ...)
"""
import collections
import os
import types

import asyncpg
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

from . import settings, romes, dbpool, library, __version__
from .routers import root_router, routers_1_0
from .hardsettings import ALLOWED_API_VERSIONS

VersionInfo = collections.namedtuple("VersionInfo", ("major", "minor"))


def create_asgi_app() -> FastAPI:
    """
    Factory d'appli ASGI

    Returns:
        Application ASGI andi-matching initialisée et paramétrée
    """
    # On bootstrape la config si nécessaire
    config = settings.config

    # Juste pour bootstrapper l'index Whoosh
    _ = romes.SUGGEST_STATE

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

    # Voir http://glenfant.github.io/flask-g-object-for-fastapi.html
    @app.middleware("http")
    async def init_requestvars(request: Request, call_next):
        # Mémorisation de la version d'API demandée pour ce request
        for part in request.url.path.split("/"):
            if part in ALLOWED_API_VERSIONS:
                api_version_info = VersionInfo._make(int(v) for v in part.split("."))
                break
        else:
            api_version_info = None
        initial_g = types.SimpleNamespace(api_version_info=api_version_info)
        library.request_global.set(initial_g)
        response = await call_next(request)
        return response

    @app.on_event("startup")
    async def startup_event():  # pylint: disable=unused-variable
        async def pool_factory():
            pool = await asyncpg.create_pool(**config.PG_CONNECTIONS_POOL)
            return pool

        # Do not initiate DB Pool when testing (AN4_NO_DB_CONNECTION is a test-environment specific variable)
        if os.getenv('AN4_NO_DB_CONNECTION', 'false') == 'false':
            await dbpool.init(pool_factory)
        else:
            await dbpool.init(dbpool.tests_pool_factory)

    app.include_router(root_router)
    for router in routers_1_0:
        app.include_router(router, prefix="/1.0", tags=["v1.0"])
    return app


app = create_asgi_app()
