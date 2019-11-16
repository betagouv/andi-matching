#!/usr/bin/env python3
import argparse
import logging
import os
import sys
from datetime import datetime

import pytz
import uvicorn
import yaml
from fastapi import FastAPI

from library import geo_code_query, get_codes
from matching import lib_match
from model_input import Model as QueryModel
from model_output import Model as ResponseModel

sys.path.append(os.path.dirname(__file__))

"""
TODO:
- return error structure
- integrate with matchn backend
- add behave testing
- monitoring
"""
VERSION = 1

# ################################################### SETUP AND ARGUMENT PARSING
# ##############################################################################
logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName('INFO'))
logger.addHandler(logging.StreamHandler())


config = {
    'postgresql': {'dsn': os.getenv('PG_DSN', 'postgress://user:pass@localhost:5432/db')},
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


# ################################################################ MATCHING FLOW
# ##############################################################################
def get_trace_obj(query):
    return {
        '_query_id': query.query_id,
        '_session_id': query.session_id,
        '_trace': 'not_implemented_yet',
    }


def get_parameters(_criteria):
    # FIXME: To be continued...
    return {
        'max_distance': 6,
        'romes': ['H2207'],
        'includes': [],
        'excludes': [],
        'sizes': ['pme'],
        'multipliers': {
            'fg': 5
        },
    }


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
    return [{
        'id': r['id'],
        'name': r['nom'],
        'address': r['adresse'],
        'departement': r['departement'],
        'city': r['commune'],
        'coords': {'lat': 93, 'lon': 18},
        'size': r['taille'],
        'naf': r['naf'],
        'siret': r['siret'],
        'distance': int(''.join(list(filter(str.isdigit, r['distance'])))),
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

    # return [{
    #     'id': '12',
    #     'name': 'Pains d\'Amandine',
    #     'address': 'ADDRESSE',
    #     'departement': '29',
    #     'city': 'Cergy',
    #     'coords': {'lat': 93.123, 'lon': 83.451},
    #     'size': 'pme',
    #     'naf': '7711A',
    #     'siret': '21398102938',
    #     'distance': 54,
    #     'scoring': {'geo': 3, 'size': 4, 'contact': 2, 'pmsmp': 3, 'naf': 5},
    #     'score': 53,
    #     'activity': 'Boulangerie',
    # }]


# ################################################################ SERVER ROUTES
# ##############################################################################
@app.get("/")
def root():
    return {"Salut le monde !"}


@app.post("/match", response_model=ResponseModel)
async def matching(query: QueryModel):
    logger.debug(query)
    trace = get_trace_obj(query)
    lat, lon = await get_address_coords(query.address)
    params = get_parameters(query.criteria)
    logger.debug('Query params: %s', params)
    raw_data = await lib_match.run_profile_async(config, lat, lon, **params)
    logger.debug('raw responses:')
    logger.debug(yaml.dump(raw_data))
    data = await make_data(raw_data)
    logger.debug('clean responses:')
    logger.debug(yaml.dump(data))
    return {
        '_v': VERSION,
        '_timestamp': datetime.now(pytz.utc),
        'data': data,
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
