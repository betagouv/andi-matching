"""
/track
"""
import json
import logging
from datetime import datetime

from fastapi import APIRouter, Request, Depends
from fastapi.encoders import jsonable_encoder

from .. import lib_db
from ..library import is_valid_uuid
from andi.webservice.schemas.tracker import Model as TrackingModel
from ..settings import config

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/track")
async def tracking(query: TrackingModel, request: Request, db=Depends(lib_db.get)):
    """
    Tracking endpoint
    """
    sql = """
    INSERT INTO trackers (
        session_id,
        version,
        send_order,
        data
    ) VALUES ($1, $2, $3, $4);
    """
    query.server_context.reception_timestamp = datetime.now()
    query.server_context.user_agent = request.headers['user-agent']

    logger.debug('Available request headers: %s', ', '.join(request.headers.keys()))
    if 'X-Real-IP' in request.headers:
        query.server_context.client_ip = request.headers['X-Real-Ip']
    else:
        query.server_context.client_ip = request.client.host

    # FIXME: IP blacklisting to be removed or refactored once proper staging / testing environment available
    if query.server_context.client_ip in config.TESTERS_IP_ADDRESSES:
        # covid update: do not track team-members from home (which for now happens by using the dev flag)
        logger.debug('Client ip %s is in hardcoded blacklist, forcing dev tag', query.server_context.client_ip)
        query.meta['dev'] = True
        query.meta['blacklisted'] = True

    if not is_valid_uuid(query.session_id):
        # Do not store nor track "ANONYMOUS" session id's
        logger.debug('Session id is not a valid UUID, skipping')
        return

    await db.execute(sql, query.session_id, query.v, query.order, json.dumps(jsonable_encoder(query)))
    logger.debug('Wrote tracking log # %s from %s', query.order, query.session_id)
