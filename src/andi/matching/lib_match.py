import json
import os
from urllib.parse import quote_plus

import psycopg2
import yaml
from andi.webservice.hardsettings import MAX_VALUE_GROUP
from andi.webservice.match import logger, selected_nafs_from_romes, get_naf_sql, parse_rome_size_prefs, get_size_rules
from psycopg2.extras import RealDictCursor

from andi.webservice import sql as SQLLIB

# from sql import MATCH_QUERY

"""
The functionality in this library mostly deals with the preparation and execution
of the final SQL query.

Two functions are provided to execute the matching query:
- one sync, used in CLI
- one async, used by the API
"""


# ##################################################################### HELPERS
# #############################################################################
def get_rome_defs(romes):
    """
    Loading NAF/ROME correspondance table
    """

    current_dir = os.path.dirname(os.path.abspath(__file__))
    out = {}
    for rome in romes:
        rome = rome.upper()
        if ':' in rome:
            rome, vgroup = rome.split(':')
        else:
            vgroup = MAX_VALUE_GROUP

        logger.debug('Loading definition for rome %s (value group: %s)', rome, vgroup)
        rome_path = f'{current_dir}/rome_defs/{rome}.yaml'
        try:
            with open(rome_path, 'r') as rome_file:
                out[rome] = yaml.safe_load(rome_file)
                out[rome]['value_group'] = vgroup
        except FileNotFoundError:
            logger.warning(
                'Definition for ROME %s not found (does file %s exist ?)',
                rome,
                rome_path
            )

    return out


def parse_naf_list(naf_defs, include=None, exclude=None):  # pylint: disable=too-many-branches
    include = set() if not include else include
    exclude = set() if not exclude else exclude

    codes = {str(i): set() for i in range(1, int(MAX_VALUE_GROUP) + 1)}
    domains = {str(i): set() for i in range(1, int(MAX_VALUE_GROUP) + 1)}

    for naf in include:
        codes[MAX_VALUE_GROUP].add(naf)

    # def clean(l, n):
    #     if n in l:
    #         l.remove(n)

    for _rome, d in naf_defs.items():
        vgroup = int(d['value_group'])
        if 'naf_domains_secondary' in d:
            for naf in d['naf_domains_secondary']:
                domains[str(vgroup - 1)].add(naf)
        if 'naf_domains_principal' in d:
            for naf in d['naf_domains_principal']:
                domains[str(vgroup)].add(naf)
        if 'naf_secondary' in d:
            for naf in d['naf_secondary']:
                codes[str(vgroup - 1)].add(naf)
        if 'naf_principal' in d:
            for naf in d['naf_principal']:
                codes[str(vgroup)].add(naf)

        if 'naf_of_interest' in d:
            for naf in d['naf_of_interest']:
                codes[str(vgroup)].add(naf)

    out_codes, out_domains = {}, {}
    done = set()
    for vgroup in reversed(range(1, int(MAX_VALUE_GROUP) + 1)):
        vg = str(vgroup)
        if vg in codes:
            for naf in codes[vg]:
                if naf not in done and naf not in exclude:
                    done.add(naf)
                    out_codes[naf] = vgroup
        if vg in domains:
            for dom in domains[vg]:
                if dom not in done:
                    done.add(dom)
                    out_domains[dom] = vgroup

    return out_codes, out_domains


# ####################################################################### MATCH
# #############################################################################
def run_profile(cfg, lat, lon, max_distance, romes, includes, excludes, sizes, multipliers,
                rome2naf='def'):  # pylint: disable=too-many-arguments
    """
    Standard function, used in CLI operation (too slow for real-time), deprecated
    """
    if max_distance == '':
        max_distance = 10

    if rome2naf == 'def':
        logger.debug('Naf2Rome "definition" method selected')
        naf_def = get_rome_defs(romes)
        logger.debug('Naf matching definitions:\n%s', json.dumps(naf_def, indent=2))
        naf_rules = parse_naf_list(naf_def, includes, excludes)
    elif rome2naf == 'andidata':
        logger.debug('Naf2Rome "andidata" method selected')
        naf_rules = selected_nafs_from_romes(romes, includes, excludes)
        naf_def = False

    logger.debug('Naf matching rules:\n%s', json.dumps(naf_rules, indent=2))
    naf_sql = get_naf_sql(naf_rules)
    logger.debug('Naf sql:\n%s', naf_sql)

    tpe, pme, eti, ge = parse_rome_size_prefs(
        naf_def,
        'tpe' in sizes,
        'pme' in sizes,
        'eti' in sizes,
        'ge' in sizes)

    logger.info(
        'Parsed sizes: tpe: %s, pme: %s, eti: %s, ge: %s',
        tpe,
        pme,
        eti,
        ge
    )

    size_sql = get_size_rules(tpe, pme, eti, ge)
    logger.debug('Size rules:\n%s', size_sql)

    result = {}
    logger.info('Connecting to database ...')
    with psycopg2.connect(cursor_factory=RealDictCursor, **cfg['postgresql']) as conn, conn.cursor() as cur:
        logger.info('Obtained database cursor')
        # XXX: /!\ multiplier defauls hardcoded
        data = {
            'lat': lat,
            'lon': lon,
            'dist': max_distance,
            'mul_geo': multipliers.get('fg', 1),
            'mul_naf': multipliers.get('fn', 5),
            'mul_siz': multipliers.get('ft', 3),
            'mul_wel': multipliers.get('fw', 2),
            'mul_con': multipliers.get('fc', 1),

        }
        sql = cur.mogrify(SQLLIB.MATCH_QUERY_PSYPG2.format(
            naf_rules=naf_sql,
            size_rules=size_sql,
            limit_test=f'LIMIT {cfg["limit"]}' if 'limit' in cfg else ''
        ), data)
        logger.debug(sql.decode('utf8'))
        cur.execute(sql)
        result = cur.fetchall()

    for row in result:
        # row['google_url'] = ''.join(['https://google.fr/search?q=', quote_plus(row['nom']), quote_plus(row['departement'])])
        row['andi_fiche'] = ''.join(['https://andi.beta.gouv.fr:4430/company/browse/', str(row['id'])])
        row['google_search'] = ''.join([
            'https://google.fr/search?q=',
            quote_plus(row['nom'].lower()),
            '+',
            quote_plus(str(row['departement'])),
            '+',
            quote_plus(str(row['commune'])),
        ])

    return result


