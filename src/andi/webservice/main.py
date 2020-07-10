#!/usr/bin/env python3
import argparse
import logging
import os
import pathlib

import asyncpg
import dotenv
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from . import __version__
from . import dbpool
from . import lib_rome_suggest_v2
from . import settings
from .routers import all_routers

logger = logging.getLogger(__name__)


def create_asgi_app() -> FastAPI:
    """
    Factory d'appli ASGI

    Returns:
        Application ASGI andi-matching initialisée et paramétrée
    """
    dotenv.load_dotenv(dotenv.find_dotenv(usecwd=True))
    # On bootstrape la config si nécessaire
    config = settings.config

    # Juste pour bootstrapper l'index Wooosh
    _ = lib_rome_suggest_v2.SUGGEST_STATE

    # Construction et paramétrage de l'app ASGI
    app = FastAPI(**config.FASTAPI_OPTIONS)
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


def make_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Matching server process')
    add_arg = parser.add_argument
    add_arg("-c", "--config-file", type=argparse.FileType("r"), default=None,
            help=("Fichier de configuration remplaçant celui fourni par la variable "
                  f"d'environnement {settings.CONFIG_FILE_ENNVAR}"
                  )
            )
    add_arg("--dump-config", action="store_true",
            help=("Affiche le fichier de configuration par défaut pouvant vous servir de base "
                  "à un fichier de configuration personnalisé")
            )
    add_arg("--version", action="version", version=__version__)
    return parser


def main():
    parser = make_arg_parser()
    args = parser.parse_args()
    if args.dump_config:
        defaultconfig_path = pathlib.Path(__file__).resolve().parent / "defaultsettings.py"
        print(defaultconfig_path.read_text())
        return

    # Un fichier de config person par la ligne de connande
    if args.config_file is not None:
        os.environ[settings.CONFIG_FILE_ENNVAR] = args.config_file.name
        args.config_file.close()
        settings.reset_config()
    config = settings.config
    app = create_asgi_app()
    config.UVICORN_OPTIONS["log_config"] = config.LOGGING
    uvicorn.run(
        app,
        **config.UVICORN_OPTIONS
    )


if __name__ == "__main__":
    main()
