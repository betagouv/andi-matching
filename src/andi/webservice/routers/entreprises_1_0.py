"""
/match
"""
import logging
import pprint
from typing import List

from fastapi import APIRouter, Depends

from .. import dbpool
from ..entreprises import run_profile_async
from ..library import get_parameters
from ..schemas.entreprises import EntreprisesQueryModel, EntrepriseResponse
from ..settings import config

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/entreprises", response_model=List[EntrepriseResponse],
            operation_id="rechercherEntreprises",
            summary="Recherche entreprises / établissements",
            description="Recherche d'entreprises et établissements à proximité pour une immersion.")
async def get_entreprises(query: EntreprisesQueryModel, db=Depends(dbpool.get)):
    """
    Entreprises endpoint:
    Web API for ANDi internal matching algorithm.
    """
    logger.debug(query)
    lat, lon = await query.address.get_coord()
    params = get_parameters(query.criteria)
    logger.debug('Query params: %s', params)
    raw_data = await run_profile_async(lat, lon, conn=db, limit=config.MATCHING_QUERY_LIMIT,
                                       **params)
    logger.debug('raw responses:')
    logger.debug(pprint.pformat(raw_data[:4]))
    data = make_data(raw_data)
    logger.debug('clean responses:')
    logger.debug(pprint.pformat(data[:4]))
    return data


def make_data(responses=None):
    """
    Create response data object:

    {
        'id': '12',
        'name': 'Pains d\'Amandine',
        'address': 'ADDRESSE',
        'departement': '29',
        'city': 'Cergy',
        'coords': {'lat': 93.123, 'lon': 83.451},
        'size': 'pme',
        'naf': '7711A',
        'siret': '21398102938',
        'distance': 54,
        'scoring': {'geo': 3, 'size': 4, 'contact': 2, 'pmsmp': 3, 'naf': 5},
        'score': 53,
        'activity': 'Boulangerie',
    }
    """
    return [{
        'id': resp['id'],
        'name': resp['nom'],
        'address': resp['adresse'],
        'departement': resp['departement'],
        'phonenumber': resp['phonenumber'],
        'city': resp['commune'],
        'coords': {'lat': resp["lat"], 'lon': resp["lon"]},
        'size': resp['taille'],
        'naf': resp['naf'],
        'siret': resp['siret'],
        'distance': resp['distance'],
        'scoring': {
            'geo': resp['score_geo'],
            'size': resp['score_size'],
            'naf': resp['score_naf'],
            'contact': resp['score_contact'],
            'pmsmp': resp['score_welcome'],
        },
        'score': resp['score_total'],
        'activity': resp['sector']
    } for resp in responses]
