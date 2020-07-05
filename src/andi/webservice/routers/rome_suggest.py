import logging
import uuid
from datetime import datetime
from typing import Union

import pytz
from andi.webservice.schemas.rome_suggest import Model as RomeResponseModel, InputModel as RomeInputModel
from fastapi import APIRouter
from pydantic.types import PositiveInt

from ..hardconfig import API_VERSION
from ..lib_rome_suggest_v2 import SUGGEST_STATE, match as rome_suggest
from ..library import get_trace_obj, utc_now
from ..settings import config

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/rome_suggest", response_model=RomeResponseModel)
async def api_rome_suggest(sid: Union[uuid.UUID, str] = "", q: str = "", _v: PositiveInt = 1,
                           _timestamp: datetime = False):
    """
    Rome suggestion endpoint:
    Query rome code suggestions according to input string,
    only returning top 15 results.
    """
    logger.debug('received query %s', [q])
    query_id = uuid.uuid4()
    raw_query = {
        '_v': _v,
        '_timestamp': _timestamp if _timestamp else datetime.now(pytz.utc),
        '_query_id': query_id,
        '_session_id': sid,
        'needle': q
    }
    logger.debug('Query params: %s', raw_query)
    query = RomeInputModel(**raw_query)

    trace = get_trace_obj(query)
    logger.debug('Running query...')
    rome_list = rome_suggest(query.needle, SUGGEST_STATE)
    logger.debug('Obtained %s results', len(rome_list))
    return {
        '_v': API_VERSION,
        '_timestamp': utc_now(),
        'data': rome_list[:config.ROME_SUGGEST_LIMIT],
        **trace,
    }
