"""
/match
"""
import json
import logging

from andi.matching import lib_match
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder

from .. import dbpool
from ..hardconfig import API_VERSION
from ..library import get_trace_obj, get_parameters, utc_now, is_valid_uuid
from ..schemas.match import QueryModel, ResponseModel
from ..settings import config

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/match", response_model=ResponseModel,
             summary="Recherche de sociétés",
             description="Recherche de sociétés à proximité pour une immersion.",
             tags=["public"])
async def matching(query: QueryModel, db=Depends(dbpool.get)):
    """
    Matching endpoint:
    Web API for ANDi internal matching algorithm.
    """
    logger.debug(query)
    trace = get_trace_obj(query)
    lat, lon = await query.address.get_coord()
    params = get_parameters(query.criteria)
    logger.debug('Query params: %s', params)
    raw_data = await lib_match.run_profile_async(lat, lon, conn=db, limit=config.MATCHING_QUERY_LIMIT,
                                                 **params)
    logger.debug('raw responses:')
    logger.debug(json.dumps(raw_data[:4], indent=2))
    data = await make_data(raw_data)
    logger.debug('clean responses:')
    logger.debug(json.dumps(data[:4], indent=2))

    try:
        await match_track(query, params, lat, lon, db)
    except Exception:  # pylint:disable=broad-except
        pass

    return {
        '_v': API_VERSION,
        '_timestamp': utc_now(),
        'data': data,
        **trace,
    }


async def make_data(responses=None):
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
        'coords': {'lat': 93, 'lon': 18},
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


async def match_track(query, params, lat, lon, db):
    sql = """
    INSERT INTO trackers (
        session_id,
        version,
        send_order,
        data
    ) VALUES ($1, $2, $3, $4);
    """
    if not is_valid_uuid(query.session_id):
        # Do not store nor track "ANONYMOUS" session id's
        logger.debug('Session id is not a valid UUID, skipping')
        return
    payload = {
        'page': 'api',
        'action': 'match',
        'meta': {
            'lat': lat,
            'lon': lon,
            'address': query.address,
            'criteria': query.criteria,
            'query_id': query.query_id
        }
    }
    await db.execute(sql, query.session_id, 1, 0, json.dumps(jsonable_encoder(payload)))
