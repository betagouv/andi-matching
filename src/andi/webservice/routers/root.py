"""
Route /
"""
import functools
import math
import os
import urllib.parse

from fastapi import APIRouter, Request

from .. import __version__
from ..hardsettings import START_TIME, API_VERSION
from ..library import utc_now
from ..settings import CONFIG_FILE_ENNVAR, config

router = APIRouter()


def censored_url(real_url: str) -> str:
    """
    Remplace l'éventuel mot de passe d'une URL par "xxxx"

    Args:
        real_url: L'URL à censurer

    Returns:
        L'URL censurée
    """
    parsed = urllib.parse.urlparse(real_url)
    censored_netloc = ""
    if parsed.username:
        censored_netloc += parsed.username
    if parsed.password:
        censored_netloc += ":<censored>"
    if censored_netloc:
        censored_netloc += "@"
    if parsed.hostname:
        censored_netloc += parsed.hostname
    if parsed.port:
        censored_netloc += f":{parsed.port}"
    censored_parsed = list(parsed)
    censored_parsed[1] = censored_netloc
    return urllib.parse.urlunparse(censored_parsed)


@router.get("/", operation_id="systemStatus", summary="Status",
            description="Le status du service ANDi.", tags=["system"])
def root(request: Request):
    """
    Le status du service ANDi
    """
    now = utc_now()
    delta = now - START_TIME
    delta_s = math.floor(delta.total_seconds())
    base_url = str(request.url)
    if base_url.endswith("//"):
        base_url = base_url[:-1]
    if not base_url.endswith("/"):
        base_url += "/"

    absolute_url = functools.partial(urllib.parse.urljoin, base_url)
    return {
        'all_systems': 'nominal',
        'timestamp': now,
        'start_time': START_TIME,
        'uptime': f'{delta_s} seconds | {divmod(delta_s, 60)[0]} minutes | {divmod(delta_s, 86400)[0]} days',
        'api_version': API_VERSION,
        "configuration": os.getenv(CONFIG_FILE_ENNVAR, "<default>"),
        "database": censored_url(config.PG_CONNECTIONS_POOL["dsn"]),
        "software_version": __version__,
        "base_url": base_url,
        "doc_urls": [absolute_url("docs"), absolute_url("redoc")],
        "openapi_url": absolute_url("openapi.json")
    }
