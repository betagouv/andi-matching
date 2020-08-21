"""
Routes et handlers de l'API
"""
from .root import router as root_router
from . import entreprises_1_0, romes_1_0

# Tous les routers de /1.0/xxx
routers_1_0 = (getattr(mod, "router") for mod in (entreprises_1_0, romes_1_0))
