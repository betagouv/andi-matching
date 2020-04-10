#!/usr/bin/env python3
import argparse
import json
import logging
import math
import os
import sys
import uuid
from datetime import datetime
from functools import reduce
from typing import Union

import pytz
import uvicorn
import yaml
from fastapi import Depends, FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import PositiveInt
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

import criterion_parser
# from library import get_dataframes_v1 as init_rome_suggest
# from library import rome_suggest_v1 as rome_suggest
import lib_db
from lib_rome_suggest_v2 import (
    init_state as init_rome_suggest,
    match as rome_suggest
)
from library import geo_code_query, get_codes  # rome_list_query,
from matching import lib_match
from model_entreprise import (
    InputModel as EntrepriseInputModel,
    Model as EntrepriseResponseModel
)
from model_input import Model as QueryModel
from model_output import Model as ResponseModel
from model_rome_suggest import (
    InputModel as RomeInputModel,
    Model as RomeResponseModel
)
from model_tracker import Model as TrackingModel

sys.path.append(os.path.dirname(__file__))

"""
TODO:
- monitoring
"""
VERSION = 1
START_TIME = datetime.now(pytz.utc)

DEFAULT_MATCHING_PARAMS = {
    'includes': [],
    'excludes': [],
    'sizes': ['pme'],
    'multipliers': {
        'fg': 1,  # Geo
        'fn': 5,  # Naf/Rome
        'ft': 2,  # Size
        'fw': 4,  # Welcome
        'fc': 3,  # Contact
    }
}

# ################################################### SETUP AND ARGUMENT PARSING
# ##############################################################################
logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName('INFO'))
logger.addHandler(logging.StreamHandler())


config = {
    'postgresql': {
        'dsn': os.getenv('PG_DSN', 'postgres://user:pass@localhost:5432/db'),
        'min_size': 4,
        'max_size': 20
    },
    'server': {
        'host': os.getenv('HOST', 'localhost'),
        'port': int(os.getenv('PORT', '5000')),
        'log_level': os.getenv('LOG_LEVEL', 'info'),
    },
    'force_build': os.getenv('FORCE_BUILD', 'false') == 'true',
    'log_level': os.getenv('LOG_LEVEL', 'info'),
    'proxy_prefix': os.getenv('PROXY_PREFIX', '/'),
    # FIXME: Ip blacklist currently hardcoded, this should be removed
    # once a propre staging / testing environment is available
    'ip_blacklist': [
        # local
        '::1',
        '127.0.0.1',
        # Team
        '92.141.121.208',
        '109.14.83.176',
        '78.194.230.237',
        '78.194.248.76',
        '92.184.117.65',
        '82.124.221.174',
        '87.66.113.183',
        # CDC
        '213.41.72.24',
        '90.80.178.34',
        '212.157.112.24',
        '212.157.112.26',
    ]
}

if config['log_level'] == 'debug':
    logger.setLevel(logging.getLevelName('DEBUG'))

logger.debug('Debug activated')
logger.debug('Config values: \n%s', yaml.dump(config))

app = FastAPI(openapi_prefix=config['proxy_prefix'])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

SUGGEST_STATE = init_rome_suggest(force=config['force_build'])


# ######################################################################## UTILS
# ##############################################################################
def get_trace_obj(query):
    return {
        '_query_id': query.query_id,
        '_session_id': query.session_id,
        '_trace': 'not_implemented_yet',
    }


def parse_param(accumulator, criterion):
    res = getattr(criterion_parser, criterion.name)(criterion, accumulator)
    return res


def get_parameters(criteria):
    return reduce(parse_param, criteria, DEFAULT_MATCHING_PARAMS)


async def get_address_coords(address):
    if address.type == 'string':
        addr_string = address.value
        geo_data = await geo_code_query(addr_string)
    elif address.type == 'geoapigouv':
        geo_data = address.value
    lat, lon = get_codes(geo_data)
    logger.debug('Extracted query coordinates lat %s lon %s', lat, lon)
    return lat, lon


async def make_data(responses=None):
    """
    Create response data obect:

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
        'id': r['id'],
        'name': r['nom'],
        'address': r['adresse'],
        'departement': r['departement'],
        'phonenumber': r['phonenumber'],
        'city': r['commune'],
        'coords': {'lat': 93, 'lon': 18},
        'size': r['taille'],
        'naf': r['naf'],
        'siret': r['siret'],
        'distance': r['distance'],
        # 'distance': float(''.join(list(filter(str.isdigit, r['distance'])))),
        'scoring': {
            'geo': r['score_geo'],
            'size': r['score_size'],
            'naf': r['score_naf'],
            'contact': r['score_contact'],
            'pmsmp': r['score_welcome'],
        },
        'score': r['score_total'],
        'activity': r['sector']
    } for r in responses]


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


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


# ################################################################ SERVER ROUTES
# ##############################################################################
@app.on_event("startup")
async def startup_event():
    # Do not initiate DB Pool when testing (NO_ASYNCPG is a test-environment specific variable)
    if os.getenv('NO_ASYNCPG', 'false') == 'false':
        await lib_db.init(config)


@app.get("/")
def root():
    """
    Query service status
    """
    now = datetime.now(pytz.utc)
    delta = now - START_TIME
    delta_s = math.floor(delta.total_seconds())
    return {
        'all_systems': 'nominal',
        'timestamp': now,
        'start_time': START_TIME,
        'uptime': f'{delta_s} seconds | {divmod(delta_s, 60)[0]} minutes | {divmod(delta_s, 86400)[0]} days',
        'api_version': VERSION,
    }


@app.post("/track")
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
    elif 'x-real-ip' in request.headers:
        query.server_context.client_ip = request.headers['x-real-ip']
    else:
        query.server_context.client_ip = request.client.host

    # FIXME: IP blacklisting to be removed or refactored once proper staging / testing environment available
    if query.server_context.client_ip in config['ip_blacklist']:
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


@app.post("/match", response_model=ResponseModel)
async def matching(query: QueryModel, db=Depends(lib_db.get)):
    """
    Matching endpoint:
    Web API for ANDi internal matching algorithm.
    """
    logger.debug(query)
    trace = get_trace_obj(query)
    lat, lon = await get_address_coords(query.address)
    params = get_parameters(query.criteria)
    logger.debug('Query params: %s', params)
    raw_data = await lib_match.run_profile_async(config, lat, lon, conn=db, **params)
    logger.debug('raw responses:')
    logger.debug(yaml.dump(raw_data[:4]))
    data = await make_data(raw_data)
    logger.debug('clean responses:')
    logger.debug(yaml.dump(data[:4]))

    try:
        await match_track(query, params, lat, lon, db)
    except Exception:  # pylint:disable=broad-except
        pass

    return {
        '_v': VERSION,
        '_timestamp': datetime.now(pytz.utc),
        'data': data,
        **trace,
    }


@app.get("/rome_suggest", response_model=RomeResponseModel)
async def api_rome_suggest(sid: Union[uuid.UUID, str] = "", q: str = "", _v: PositiveInt = 1, _timestamp: datetime = False):
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
    # rome_list = await rome_list_query(query.needle)
    rome_list = rome_suggest(query.needle, SUGGEST_STATE)
    logger.debug('Obtained %s results', len(rome_list))
    return {
        '_v': VERSION,
        '_timestamp': datetime.now(pytz.utc),
        'data': rome_list[:15],
        **trace,
    }


@app.get("/entreprise", response_model=EntrepriseResponseModel)
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
        '_v': VERSION,
        '_timestamp': datetime.now(pytz.utc),
        'data': employer_data,
        **trace,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Matching server process')
    parser.add_argument('--config', dest='config', help='config file', default=None)
    parser.add_argument('--debug', dest='debug', action='store_true', default=False, help='Debug mode')
    parser.add_argument('--force-build', dest='forceBuild', action='store_true', default=False, help='Force rebuilding of suggest db')
    args = parser.parse_args()
    if args.debug:
        logger.debug('Debug activated')
        config['log_level'] = 'debug'
        config['server']['log_level'] = 'debug'
        logger.debug('Arguments: %s', args)

    uvicorn.run(
        app,
        **config['server']
    )
