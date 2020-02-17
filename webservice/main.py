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

import asyncpg
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
COUNTER = 0
SUGGEST_COUNTER = 0

DEFAULT_MATCHING_PARAMS = {
    'includes': [],
    'excludes': [],
    'sizes': ['pme'],
    'multipliers': {
        'fg': 1,
        'fn': 5,
        'ft': 3,
        'fw': 2,
        'fc': 1,
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
    'log_level': os.getenv('LOG_LEVEL', 'info'),
    'proxy_prefix': os.getenv('PROXY_PREFIX', '/'),
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

SUGGEST_STATE = init_rome_suggest()

DB_POOL = []


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


async def get_db():
    global DB_POOL
    conn = await DB_POOL.acquire()
    try:
        yield conn
    finally:
        await DB_POOL.release(conn)


# ################################################################ SERVER ROUTES
# ##############################################################################
@app.on_event("startup")
async def startup_event():
    global DB_POOL
    if os.getenv('NO_ASYNCPG', 'false') == 'false':
        DB_POOL = await asyncpg.create_pool(**config['postgresql'])


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
        'api_counter': COUNTER,
        'api_suggest_counter': SUGGEST_COUNTER,
    }


@app.post("/track")
async def matching(query: TrackingModel, request: Request, db=Depends(get_db)):
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
    query.server_context.client_ip = request.client.host
    query.server_context.user_agent = request.headers['user-agent']
    await db.execute(sql, query.session_id, query.v, query.order, json.dumps(jsonable_encoder(query)))
    logger.debug('Wrote tracking log # %s from %s', query.order, query.session_id)


@app.post("/match", response_model=ResponseModel)
async def matching(query: QueryModel, db=Depends(get_db)):
    """
    Matching endpoint:
    Web API for ANDi internal matching algorithm.
    """
    global COUNTER  # pylint:disable=global-statement
    COUNTER += 1
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
    return {
        '_v': VERSION,
        '_timestamp': datetime.now(pytz.utc),
        'data': data,
        **trace,
    }


@app.get("/rome_suggest", response_model=RomeResponseModel)
async def api_rome_suggest(_sid: uuid.UUID, q: str = "", _v: PositiveInt = 1, _timestamp: datetime = False):
    """
    Rome suggestion endpoint:
    Query rome code suggestions according to input string,
    only returning top 15 results.
    """
    global SUGGEST_COUNTER  # pylint:disable=global-statement
    SUGGEST_COUNTER += 1
    query_id = uuid.uuid4()
    raw_query = {
        '_v': _v,
        '_timestamp': _timestamp if _timestamp else datetime.now(pytz.utc),
        '_query_id': query_id,
        '_session_id': _sid,
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
