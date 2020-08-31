"""
Routes et handlers de l'API
"""
from . import root, match, romesuggest

# Tous les routers accessibles depuis de sous-package
all_routers = (getattr(mod, "router") for mod in (root, match, romesuggest))
