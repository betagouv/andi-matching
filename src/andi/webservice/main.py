#!/usr/bin/env python3
import argparse
import logging
import os
import pathlib

import uvicorn

from . import __version__
from . import hardsettings
from . import settings

logger = logging.getLogger(__name__)

BANNER = r"""
  ,---.  ,--.  ,--.,------.  ,--.         ,---.  ,------. ,--.
 /  O  \ |  ,'.|  ||  .-.  \ `--',-----. /  O  \ |  .--. '|  |
|  .-.  ||  |' '  ||  |  \  :,--.'-----'|  .-.  ||  '--' ||  |
|  | |  ||  | `   ||  '--'  /|  |       |  | |  ||  | --' |  |
`--' `--'`--'  `--'`-------' `--'       `--' `--'`--'     `--'
"""


def make_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Matching server process')
    add_arg = parser.add_argument
    add_arg("-c", "--config-file", type=argparse.FileType("r"), default=None,
            help=("Fichier de configuration remplaçant celui fourni par la variable "
                  f"d'environnement {hardsettings.CONFIG_FILE_ENNVAR}"
                  )
            )
    add_arg("--dump-default-config", action="store_true",
            help=("Affiche le fichier de configuration par défaut pouvant vous servir de base "
                  "à un fichier de configuration personnalisé")
            )
    add_arg("--version", action="version", version=__version__)
    return parser


def main():
    parser = make_arg_parser()
    args = parser.parse_args()
    if args.dump_default_config:
        defaultconfig_path = pathlib.Path(__file__).resolve().parent / "defaultsettings.py"
        print(defaultconfig_path.read_text())
        return

    # Un fichier de config personnel par la ligne de commande
    if args.config_file is not None:
        os.environ[hardsettings.CONFIG_FILE_ENNVAR] = args.config_file.name
        args.config_file.close()
        settings.reset_config()
    config = settings.config
    print(BANNER)
    print(f"Version {__version__}")

    # Notez que l'import ici est intentionnel. Ne le remettez pas en tête de module
    # Certaines initialisation doivent s'effectuer le plus tard possible
    from .asgi import app  # pylint: disable=import-outside-toplevel
    config.UVICORN_OPTIONS["log_config"] = config.LOGGING
    uvicorn.run(
        app,
        **config.UVICORN_OPTIONS
    )


if __name__ == "__main__":
    main()
