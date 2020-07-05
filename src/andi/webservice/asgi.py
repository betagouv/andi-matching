"""
Fournit l'objet app pour un moteur ASGI (uvicorn, ...)
"""

from .main import create_asgi_app

app = create_asgi_app()
