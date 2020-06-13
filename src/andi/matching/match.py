#!/usr/bin/env python3
import csv
import json
import logging
import os

import click
import yaml

from . import exec_drive
from . import lib_match

logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName('INFO'))
logger.addHandler(logging.StreamHandler())

"""
Usage:
./match.py --lat 32.1344 --lon 5.1213 --rome ROME1 --rome ROME2

Each rome code has a NAF definition file, used for scoring naf/rome adequacy


This code was used in the beginning of ANDi, when execution was in batch.
Nowadays, an API provides this functionality, and this bit has been deprecated.

Multiple input types had been added progressively, culminating in an integration
with a Google Drive Spreadsheet, acting as front-end to the applicaiton.
"""


def cfg_get(config=''):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    defpath = f'{current_dir}/config.default.yaml'
    optpath = f'{current_dir}/{config}'
    def_config_file = open(defpath, 'r')
    opt_config_file = open(optpath, 'r') if os.path.exists(optpath) else None
    def_config = yaml.safe_load(def_config_file)
    config = {} if not opt_config_file else yaml.safe_load(opt_config_file)
    return {**def_config, **config}


def show_results(res):
    print('Obtained results preview (score is naf / size / geo / welcome / contact):')
    for row in res[:20]:
        score = f"({row['score_naf']}-{row['score_size']}-{row['score_geo']}-{row['score_welcome']}-{row['score_contact']} => {row['score_total']})"
        print(f"{row['naf']}  {row['nom']:32.30}\t{row['sector']:35.37}\t{row['distance']}\t{score}\t{row['id']}")


# ################################################################### MAIN FLOW
# #############################################################################
@click.group()
@click.option('--config_file', default=None)
@click.option('--debug', is_flag=True, default=False)
@click.option('--limit', help="Limit output rows (testing only)", default=False)
@click.pass_context
def main(ctx, config_file, debug, limit):
    if debug:
        logger.setLevel(logging.getLevelName('DEBUG'))
        logger.debug('Debugging enabled')
        ctx.obj['debug'] = True
    else:
        ctx.obj['debug'] = False

    ctx.obj['cfg'] = cfg_get(config_file)
    logger.debug('Loaded Config:\n%s', json.dumps(ctx.obj['cfg'], indent=2))

    if limit:
        logger.warning('Output Limiter set to %s', limit)
        ctx.obj['cfg']['limit'] = limit


@main.command()
@click.pass_context
def list_drive(ctx):
    profiles = exec_drive.get_data(ctx.obj['cfg'])
    logger.info('Outputting available profiles')
    print(json.dumps(list(profiles.keys()), indent=2))


@main.command()
@click.pass_context
@click.option('--profile', help="specify profile(s)", multiple=True, default=None)
@click.option('--list', 'list_flag', is_flag=True, default=False)
def run_drive(ctx, profile, list_flag):
    logger.info('Getting settings from google drive')
    profiles = exec_drive.get_data(ctx.obj['cfg'])

    if list_flag:
        profiles = exec_drive.get_data(ctx.obj['cfg'])
        logger.info('Outputting available profiles')
        print(json.dumps(list(profiles.keys()), indent=2))
        return

    results = {}
    for k, params in profiles.items():
        if profile and k not in profile:
            continue
        logger.info('Running match for profile %s', k)
        logger.debug(json.dumps(params, indent=2))
        try:
            results[k] = lib_match.run_profile(ctx.obj['cfg'], **params)
            if ctx.obj['debug']:
                show_results(results[k][:20])
        except Exception as e:
            logger.exception(e)
            logger.warning('Failed parsing profile %s, skipping', k)

    for key, result in results.items():
        keys = result[0].keys()
        temp_file = f'../output/{key}.csv'
        with open(temp_file, 'w') as output_csv:
            dwriter = csv.DictWriter(output_csv, keys)
            dwriter.writeheader()
            dwriter.writerows(result)
        logger.info('CSV file %s written', temp_file)


@main.command()
@click.option('--csv-file', help="output csv file", default='output.csv')
@click.option('--lat', help="latitude", default='49.0619')
@click.option('--lon', help="longitude", default='2.0861')
@click.option('--max-distance', help="Max distance (km)", default=10)
@click.option('--rome', help="rome code", multiple=True, default=None)
@click.option('--rome2naf', help="rome 2 naf method", default='def')
@click.option('--include', help="Include naf code", multiple=True, default=None)
@click.option('--exclude', help="Exclude naf code", multiple=True, default=None)
@click.option('--tpe/--no-tpe', help="Include 'Très Petites Entreprises' < 10 pers", default=None)
@click.option('--pme/--no-pme', help="Include 'Petites et Moyennes Entreprises' 10 - 249 pers", default=None)
@click.option('--eti/--no-eti', help="Include 'Entreprises de Taille Intermédiaire' 250 - 4999 pers", default=None)
@click.option('--ge/--no-ge', help="Include 'Grandes Entreprises' > 5000 pers", default=None)
@click.pass_context
def run_csv(ctx, csv_file, lat, lon, max_distance, rome, rome2naf, include, exclude, tpe, pme, eti, ge):
    cfg = ctx.obj['cfg']
    logger.info(
        'Matching started, lat/lon %s/%s, max %s km, ROME: %s',
        lat,
        lon,
        max_distance,
        ', '.join(rome),
    )

    sizes = []
    if tpe:
        sizes.append('tpe')
    if pme:
        sizes.append('pme')
    if eti:
        sizes.append('eti')
    if ge:
        sizes.append('ge')

    multipliers = {
        'fn': 5,
        'fg': 1,
        'ft': 3,
        'fw': 3,
        'fc': 3,
    }

    results = lib_match.run_profile(cfg, lat, lon, max_distance, rome, include, exclude, sizes, multipliers, rome2naf)

    show_results(results[:20])

    keys = results[0].keys()
    with open(csv_file, 'w') as output_csv:
        dwriter = csv.DictWriter(output_csv, keys)
        dwriter.writeheader()
        dwriter.writerows(results)
        logger.info('CSV file %s written', csv_file)


if __name__ == '__main__':
    main(obj={})  # pylint:disable=no-value-for-parameter, unexpected-keyword-arg