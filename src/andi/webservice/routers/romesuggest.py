import logging
import uuid
from datetime import datetime
from typing import Union

from andi.webservice.schemas.rome_suggest import QueryModel, ResponseModel
from fastapi import APIRouter
from pydantic.types import PositiveInt

from ..hardconfig import API_VERSION
from ..library import get_trace_obj, utc_now, awaitable_blocking
from ..romesuggest import SUGGEST_STATE, match as rome_suggest
from ..settings import config

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/rome_suggest", response_model=ResponseModel,
            summary="Suggestions ROME",
            description="Suggère des codes ROME et métiers en fonction d'un pattern de nom de métier",
            tags=["public"])
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
        '_timestamp': _timestamp or utc_now(),
        '_query_id': query_id,
        '_session_id': sid,
        'needle': q
    }
    logger.debug('Query params: %s', raw_query)
    query = QueryModel(**raw_query)

    trace = get_trace_obj(query)
    logger.debug('Running query...')
    rome_list = await awaitable_blocking(rome_suggest, query.needle, SUGGEST_STATE)
    logger.debug('Obtained %s results', len(rome_list))
    return {
        '_v': API_VERSION,
        '_timestamp': utc_now(),
        'data': rome_list[:config.ROME_SUGGEST_LIMIT],
        **trace,
    }
