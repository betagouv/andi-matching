#!/usr/bin/env python3
import argparse
# from matching import lib_match
import logging
import os
import sys
from datetime import datetime

import pytz
import uvicorn
import yaml
from fastapi import FastAPI

from model_input import Model as QueryModel
from model_output import Model as ResponseModel
from library import (
    geo_code_query
)

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
    'pg': {'dsn': os.getenv('DSN', 'postgress://user:pass@localhost:5432/db')},
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
    return {
        'max_distance': 10,
        'romes': ['1823'],
        'includes': [],
        'excludes': [],
        'sizes': [],
    }


async def get_address_coords(address):
    if address.type == 'string':
        addr_string = address.content
        geo_data = await geo_code_query(addr_string)
    elif address.type == 'geoapigouv':
        geo_data = address.content
    lat, lon = geo_data['features'][0]['geometry']['coordinates']
    logger.debug('Extracted query coordinates lat %s lon %s', lat, lon)
    return lat, lon


async def make_data(_responses=None):
    return [{
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
    }]


# ################################################################ SERVER ROUTES
# ##############################################################################
@app.get("/")
def root():
    return {"Salut le monde !"}


@app.post("/match", response_model=ResponseModel)
async def matching(query: QueryModel):
    trace = get_trace_obj(query)
    # lat, lon = await get_address_coords(query.address)
    # params = get_parameters(query.criteria)
    # raw_data = await lib_match.run_profile_async(config, lat, lon, **params)
    data = await make_data()
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
