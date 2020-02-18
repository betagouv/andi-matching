import csv
import json
import logging
import os
from collections import OrderedDict
from urllib.parse import quote_plus

import psycopg2
import yaml
from psycopg2.extras import RealDictCursor

from . import sql as SQLLIB

# from sql import MATCH_QUERY

logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName('DEBUG'))
logger.addHandler(logging.StreamHandler())

MAX_VALUE_GROUP = '5'

ANDIDATA_FILE = 'andi_rome2naf_20200130'


# ##################################################################### HELPERS
# #############################################################################
def get_rome_defs(romes):
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


def parse_rome_size_prefs(rome_defs, tpe, pme, eti, ge):
    base = OrderedDict([
        ('tpe', tpe),
        ('pme', pme),
        ('eti', eti),
        ('ge', ge)
    ])
    if rome_defs:
        for rome, d in rome_defs.items():
            if 'preferred_size' in d and d['preferred_size'] is not None:
                logger.info('ROME %s preferred sizes: %s', rome, ', '.join(d['preferred_size']))
                for t in d['preferred_size']:
                    base[t] = True if base[t] is None else base[t]

    base = {k: False if v is None else v for k, v in base.items()}

    return base.values()


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


def get_andidata_naflist(romes, include=None, exclude=None):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filename = f"{current_dir}/data_files/{ANDIDATA_FILE}.csv"
    include_list = []
    exclude_list = []
    with open(filename) as csvfile:
        rdr = csv.DictReader(
            csvfile,
            delimiter=',',
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,
        )
        for row in rdr:
            if row['rome'] in romes:
                include_list.append(row)
            if include and row['rome'] in include:
                include_list.append(row)
            if exclude and row['rome'] in exclude:
                exclude_list.append(row['naf'])

    include_list[:] = [el for el in include_list if el['naf'] not in exclude_list]
    logger.debug('raw naflist: %s', include_list)

    out_list = {x['naf']: x['score'] for x in include_list}

    return [out_list, {}]


def get_naf_sql(rules):
    '''
    Get sql rules to select naf code
    '''
    codes, domains = rules
    sql = []

    if codes:
        sql.append('CASE e.naf')
        for naf, value in codes.items():
            sql.append(f'WHEN \'{naf}\' THEN {value}')

        if domains:
            sql.append('ELSE CASE substring(e.naf, 0, 3)')
            for naf, value in domains.items():
                value -= 1
                sql.append(f'WHEN \'{naf}\' THEN {value}')
        sql.append('ELSE 1')
        if domains:
            sql.append('END')
        sql.append('END')
        return "\n".join(sql)
    if domains:
        sql.append('CASE substring(e.naf, 0, 3)')
        for naf, value in domains.items():
            value -= 1
            sql.append(f'WHEN \'{naf}\' THEN {value}')
        sql.append('ELSE 1')
        sql.append('END')
        return "\n".join(sql)
    return "1"


def sub_maxvg(vg, num):
    if num >= int(vg):
        return '1'
    return str(int(vg) - num)


def get_size_rules(tpe, pme, eti, ge):  # pylint: disable=too-many-locals
    # < 10 pers
    tpe_def = {
        '1-2': 0,
        '3-5': 0,
        '6-9': 0,
        '10-19': 1,
        '20-49': 1,
        '50-99': 1,
        '100-199': 2,
        '200-249': 2,
        '250-499': 3,
        '500-999': 4,
        '1000-1999': 5,
        '2000-4999': 6,
        '5000-9999': 7,
        '+10000': 8
    }
    # 10-249 pers
    pme_def = {
        '1-2': 3,
        '3-5': 2,
        '6-9': 1,
        '10-19': 0,
        '20-49': 0,
        '50-99': 0,
        '100-199': 0,
        '200-249': 0,
        '250-499': 1,
        '500-999': 1,
        '1000-1999': 2,
        '2000-4999': 3,
        '5000-9999': 4,
        '+10000': 5
    }
    # 250-4999 pers
    eti_def = {
        '1-2': 5,
        '3-5': 4,
        '6-9': 3,
        '10-19': 3,
        '20-49': 2,
        '50-99': 2,
        '100-199': 1,
        '200-249': 1,
        '250-499': 0,
        '500-999': 0,
        '1000-1999': 0,
        '2000-4999': 0,
        '5000-9999': 1,
        '+10000': 2
    }
    # > 5000 pers
    ge_def = {
        '1-2': 9,
        '3-5': 9,
        '6-9': 8,
        '10-19': 7,
        '20-49': 6,
        '50-99': 5,
        '100-199': 4,
        '200-249': 3,
        '250-499': 2,
        '500-999': 2,
        '1000-1999': 1,
        '2000-4999': 1,
        '5000-9999': 0,
        '+10000': 0
    }
    keys = ['1-2', '3-5', '6-9', '10-19', '20-49',
            '50-99', '100-199', '200-249', '250-499',
            '500-999', '1000-1999', '2000-4999',
            '5000-9999', '+10000']
    root = {k: int(MAX_VALUE_GROUP) for k in keys}

    loop = [(tpe, tpe_def), (pme, pme_def), (eti, eti_def), (ge, ge_def)]
    for (check, definition) in loop:
        if not check:
            continue
        for k, v in definition.items():
            root[k] = v if root[k] > v else root[k]

    root = {k: sub_maxvg(MAX_VALUE_GROUP, v) for k, v in root.items()}

    sql = []
    for k, v in root.items():
        sql.append(f'WHEN \'{k}\' THEN {v}')

    if len(sql) > 0:
        sql.append('ELSE 1')
    else:
        sql.append('WHEN TRUE THEN 1')

    return "\n".join(sql)


# https://github.com/PieterjanMontens/pgware/blob/master/pgware/utils.py
def ps2pg(q_in, v_in):
    """
    Convert psycopg2 query argument syntax to postgresql syntax
    - supports named arguments
    - keeps order of values
    - multiple reference will result in multiple values, cost of uniqueness check not worth it
    """
    if isinstance(v_in, dict):
        return ps2pg_dict(q_in, v_in)
    if not isinstance(v_in, tuple):
        v_in = [v_in]
    q_out = []
    v_out = []
    arg_count = 0
    skip = False
    for i, elm in enumerate(q_in):
        if skip and elm == 's':
            skip = not skip
        elif elm == '%' and q_in[i + 1] == 's':
            arg_count += 1
            skip = not skip
            q_out.append(f'${arg_count}')
            v_out.append(v_in[arg_count - 1])
        else:
            q_out.append(elm)
    if skip:
        raise RuntimeError('Query argument converter failed: check query')
    return ''.join(q_out), tuple(v_out)


def ps2pg_dict(q_in, v_in):
    q_out = []
    v_out = []
    skip = False
    buff = []
    for i, elm in enumerate(q_in):
        if skip and elm in ['(', ')']:
            pass
        elif skip and q_in[i - 1:i + 1] == ')s':
            v_out.append(v_in[''.join(buff)])
            q_out.append(str(len(v_out)))
            buff = []
            skip = not skip
        elif skip:
            buff.append(elm)
        elif elm == '%' and q_in[i + 1] == '(':
            q_out.append('$')
            skip = not skip
        else:
            q_out.append(elm)
    if skip:
        raise RuntimeError('Query argument converter failed: check query')
    return ''.join(q_out), tuple(v_out)


# ####################################################################### MATCH
# #############################################################################
def run_profile(cfg, lat, lon, max_distance, romes, includes, excludes, sizes, multipliers, rome2naf='def'):  # pylint: disable=too-many-arguments
    if max_distance == '':
        max_distance = 10

    if rome2naf == 'def':
        logger.debug('Naf2Rome "definition" method selected')
        naf_def = get_rome_defs(romes)
        logger.debug('Naf matching definitions:\n%s', json.dumps(naf_def, indent=2))
        naf_rules = parse_naf_list(naf_def, includes, excludes)
    elif rome2naf == 'andidata':
        logger.debug('Naf2Rome "andidata" method selected')
        naf_rules = get_andidata_naflist(romes, includes, excludes)
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


async def run_profile_async(cfg, lat, lon, max_distance, romes, includes, excludes, sizes, multipliers, conn=False):  # pylint: disable=too-many-arguments
    """
    Async optimized version of run_profile, for web server usage
    """
    if max_distance == '':
        max_distance = 10

    logger.debug('Naf2Rome "andidata" method selected')
    naf_rules = get_andidata_naflist(romes, includes, excludes)
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

    size_sql = get_size_rules(tpe, pme, eti, ge)
    logger.debug('Size rules:\n%s', size_sql)

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
    sql, params = ps2pg(SQLLIB.MATCH_QUERY.format(
        naf_rules=naf_sql,
        size_rules=size_sql,
        limit_test=f'LIMIT {cfg["limit"]}' if 'limit' in cfg else ''
    ), data)

    logger.debug("Obtained SQL:\n%s\n\n parameters:\n%s", sql, params)
    raw_result = await conn.fetch(sql, *params)
    result = [dict(row) for row in raw_result]

    return result
