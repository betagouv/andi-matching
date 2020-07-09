"""
Route /
"""
import math
import os

from fastapi import APIRouter

from .. import __version__
from ..hardconfig import START_TIME, API_VERSION
from ..library import utc_now
from ..settings import CONFIG_FILE_ENNVAR

router = APIRouter()


@router.get("/")
def root():
    """
    Le status du service
    """
    now = utc_now()
    delta = now - START_TIME
    delta_s = math.floor(delta.total_seconds())
    return {
        'all_systems': 'nominal',
        'timestamp': now,
        'start_time': START_TIME,
        'uptime': f'{delta_s} seconds | {divmod(delta_s, 60)[0]} minutes | {divmod(delta_s, 86400)[0]} days',
        'api_version': API_VERSION,
        "configuration": os.getenv(CONFIG_FILE_ENNVAR, "<default>"),
        "software_version": __version__
    }
