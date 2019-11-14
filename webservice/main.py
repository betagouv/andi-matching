#!/usr/bin/env python3
import uvicorn
from fastapi import FastAPI
from matching import lib_match
import logging
import argparse
import yaml
import os, sys
sys.path.append(os.path.dirname(__file__))
from model_output import Model as ResponseModel
from model_input import Model as QueryModel


# ################################################### SETUP AND ARGUMENT PARSING
# ##############################################################################
def cfg_get(config=None):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    defpath = f'{current_dir}/config.default.yaml'
    optpath = f'{current_dir}/{config}'
    def_config_file = open(defpath, 'r')
    opt_config_file = open(optpath, 'r') if config else None
    def_config = yaml.safe_load(def_config_file)
    config = {} if not opt_config_file else yaml.safe_load(opt_config_file)
    return {**def_config, **config}


logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName('INFO'))
logger.addHandler(logging.StreamHandler())

parser = argparse.ArgumentParser(description='Matching server process')
parser.add_argument('--config', dest='config', help='config file', default=None)
parser.add_argument('--debug', dest='debug', action='store_true', default=False, help='Debug mode')
args = parser.parse_args()

if args.debug:
    logger.setLevel(logging.getLevelName('DEBUG'))
    logger.debug('Debug activated')
    logger.debug('Arguments: %s', args)

app = FastAPI()
config = cfg_get(args.config)
logger.debug('Config values: \n%s', yaml.dump(config))

# ################################################################ MATCHING FLOW
# ##############################################################################


# ################################################################ SERVER ROUTES
# ##############################################################################
@app.get("/")
def root():
    return {"Salut le monde !"}


@app.post("/match", response_model=ResponseModel)
async def matching(query: QueryModel):
    return {"coucou"}

if __name__ == "__main__":
    uvicorn.run(
        app,
        **config['server']
    )
