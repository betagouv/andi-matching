"""
Service de configuration de andi-matching
"""

import pathlib
import types
import typing as t
import pyflexconfig

from .hardconfig import CONFIG_FILE_ENNVAR

_config = types.SimpleNamespace()
_defaultsettings_path = pathlib.Path(__file__).resolve().parent / "defaultsettings.py"


def reset_config():
    """
    Artifice permettant de forcer la re-lecture du pseudo-global ``config``
    depuis le ou les fichiers.
    """
    global _config
    _config = types.SimpleNamespace()


def __getattr__(name: str) -> t.Any:
    """Lazy loading of the config object"""
    global _config
    if name == "config":
        if len(vars(_config)) == 0:
            pyflexconfig.bootstrap(_config, defaults_path=_defaultsettings_path,
                                   custom_path_envvar=CONFIG_FILE_ENNVAR)
        return _config
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

