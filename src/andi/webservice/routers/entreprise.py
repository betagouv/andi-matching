"""
/entreprise
"""
import logging
import uuid
from datetime import datetime

import pytz
from fastapi import APIRouter
from pydantic.types import PositiveInt

from ..hardconfig import API_VERSION
from ..library import get_trace_obj
from ..schemas.entreprise import Model as EntrepriseResponseModel, InputModel as EntrepriseInputModel

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/entreprise", response_model=EntrepriseResponseModel)
async def api_entreprise(_sid: uuid.UUID, siret: str, _v: PositiveInt = 1, _timestamp: datetime = False):
    """
    Employer data endpoint
    """
    query_id = uuid.uuid4()
    raw_query = {
        '_v': _v,
        '_timestamp': _timestamp if _timestamp else datetime.now(pytz.utc),
        '_query_id': query_id,
        '_session_id': _sid,
        'siret': siret
    }
    logger.debug('Query params: %s', raw_query)
    query = EntrepriseInputModel(**raw_query)

    trace = get_trace_obj(query)
    logger.debug('Running query...')
    employer_data = {
        'siret': '18002002600019',
        'name': 'CAISSE DES DEPOTS ET CONSIGNATIONS',
        'lat': 48.8573,
        'lon': 2.3204,
        'sector': 'Autres intermédiations monétaires',
        'naf': '6419Z',
        'size': '2000-4999',
        'street_address': '56 Rue de Lille, 75007 Paris',
        'flags': []
    }
    return {
        '_v': API_VERSION,
        '_timestamp': datetime.now(pytz.utc),
        'data': employer_data,
        **trace,
    }
