"""
Tests de andi.webservice.settings
"""
import os
import types

from andi.webservice.hardconfig import CONFIG_FILE_ENNVAR
import andi.webservice.settings as settings


def test_default_settings(caplog):
    settings._config = types.SimpleNamespace()
    config = settings.config
    assert len(vars(config)) > 0
    assert not config.DEBUG


def test_custom_settings(data_directory):
    settings._config = types.SimpleNamespace()
    os.environ[CONFIG_FILE_ENNVAR] = str(data_directory / "customconfig.py")
    config = settings.config
    assert config.DEBUG
