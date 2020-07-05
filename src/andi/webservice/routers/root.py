"""
/
"""
import math

from fastapi import APIRouter

from ..hardconfig import START_TIME, API_VERSION
from ..library import utc_now

router = APIRouter()


@router.get("/")
def root():
    """
    Query service status
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
    }
