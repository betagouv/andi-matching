"""
Routes et handlers de l'API
"""
from . import root, entreprise, match, rome_suggest, track

# Tous les routers accessibles depuis de sous-package
all_routers = (getattr(mod, "router") for mod in (root, entreprise, match, rome_suggest, track))
