"""
Worker ASGI pour permettre à Uvicorn d'honorer la variable d'environnement standard
WSGI SCRIPT_NAME qui indique sous quel path l'appli est publiée
Attention : il faudra sans doute supprimer ceci si une version future d'Uvicorn tient compte de
la variable d'environnement SCRIPT_NAME.
Voir https://github.com/Midnighter/fastapi-mount/tree/root-path pour plus d'explications
Attention : ceci n'est pas à proprement parler un module de l'appli et ne peut pas être
testé sans la chaîne gunicorn -> uvicorn
"""
import os

from uvicorn.workers import UvicornWorker as OriginalWorker


class UvicornWorker(OriginalWorker):
    # https: // www.uvicorn.org / settings /
    # Equivalent des paramètres de ligne de commande Uvicorn qui ne peuvent pas
    # être passés en tant que worker pour Gunicorn
    CONFIG_KWARGS = {
        **OriginalWorker.CONFIG_KWARGS,
        "root_path": os.getenv("SCRIPT_NAME", ""),
        "proxy_headers": True
    }
