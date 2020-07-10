"""
Configuration par défaut de l"application

Note:
    N'importez pas directement depuis ce module.
    Utilisez l'objet ``config`` du module ``settings``
"""
import os

DEBUG = False

# Paramètre d'initialisation du pool de connexions PostgreSQL
# Voir la fonction asyncpg.pool.create_pool ici :
# https://magicstack.github.io/asyncpg/current/api/index.html#asyncpg.pool.create_pool
PG_CONNECTIONS_POOL = {
    "dsn": os.getenv("AN4_PG_DSN", "postgres://user:pass@localhost:5432/db"),
    "min_size": 4,
    "max_size": 20
}

# Paramètres d'initialisation du serveur Uvicorn de développement
# Voir la fonction uvicorn.run ici :
# https://www.uvicorn.org/settings/
_defautl_log_level = "debug" if DEBUG else "info"
UVICORN_OPTIONS = {
    "host": os.getenv("AN4_UVICORN_HOST", "localhost"),
    "port": int(os.getenv("AN4_UVICORN_PORT", "5000")),
    "log_level": os.getenv("AN4_UVICORN_LOG_LEVEL", _defautl_log_level),
}

# Paramètres d'initialisation de l'application FastAPI
# Voir le constructeur fastapi.FastAPI en plaçant la commande :
# python -c "import fastapi; help(fastapi.FastAPI)"
FASTAPI_OPTIONS = {
    "debug": DEBUG,
    "root_path": "/"
}

# Les visiteurs provenant de ces adresses IP sont des développeurs ou intégrateurs
TESTERS_IP_ADDRESSES = {
    # local
    '::1', '127.0.0.1',
    # Team
    '109.14.83.176', '78.194.230.237', '78.194.248.76', '82.124.221.174', '87.66.113.183', '92.141.121.208',
    '92.184.117.65',
    # CDC
    '212.157.112.24', '212.157.112.26', '213.41.72.24', '90.80.178.34'
}

# Un nombre entier pour limiter les résultats de /match
MATCHING_QUERY_LIMIT = None

# Limite de résultats retournés par le endpoint /rome_suggest
ROME_SUGGEST_LIMIT = 15

# Force la reconstruction de l'index des suggestions ROME
# Note: cet index est quand même reconstruit s'il n'existe pas.
REBUILD_SUGGEST_STATE = False

# Configuration générale de logging
# voir la fonction mogging.config.dictconfig ici :
# https://docs.python.org/3/library/logging.config.html#logging.config.dictConfig
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "()": "logging.Formatter",
            "fmt": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "standard"
        },
        "file": {
            "level": _defautl_log_level.upper(),
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.getenv("AN4_LOG_FILE", "andi.log"),
            "maxBytes": 1024 ** 2,
            "backupCount": 4,
            "formatter": "standard"
        }
    },
    "loggers": {
        "": {
            "level": _defautl_log_level.upper(),
            "handlers": ["console"]
        }
    }
}
