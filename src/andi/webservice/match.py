"""
Algotithme de "match"
"""
import csv
import json
import logging
import os
from collections import OrderedDict
from typing import Tuple, Dict, Container, Iterable

from . import sql as SQLLIB
from .hardsettings import ROME2NAF_CSV_FILE, MAX_VALUE_GROUP

logger = logging.getLogger(__name__)


async def run_profile_async(lat, lon, max_distance,  # pylint: disable=too-many-arguments,too-many-locals
                            romes, includes, excludes, sizes, multipliers, conn=False, limit=None):
    """
    Async optimized version of run_profile, for real-time web server usage
    """
    if max_distance == '':
        max_distance = 10

    logger.debug('Naf2Rome "andidata" method selected')
    # FIXME: Rendre asynchrone (actuellement blocage de l'event loop)
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
        'mul_con': multipliers.get('fc', 1)
    }
    sql, params = ps2pg(SQLLIB.MATCH_QUERY.format(
        naf_rules=naf_sql,
        size_rules=size_sql,
        limit_test=f'LIMIT {limit}' if limit else ''
    ), data)

    logger.debug("Obtained SQL:\n%s\n\n parameters:\n%s", sql, params)
    result = await conn_fetch(conn, sql, *params)
    return result


async def conn_fetch(conn, sql, *params):
    """Bien plus facile à Mocker pout les tests unitaires"""
    raw_results = await conn.fetch(sql, *params)
    return [dict(row) for row in raw_results]


def selected_nafs_from_romes(
        romes: Container[str], include: Container[str] = None,
        exclude: Container[str] = None) -> Tuple[Dict[str, str], Dict]:
    """

    Args:
        romes: Liste de code ROME
        include: Liste de codes ROME supplémentaires (?)
        exclude: Liste de codes ROME à exclure

    Returns:
        Un dict de codes NAF avec les scores.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filename = f"{current_dir}/data_files/{ROME2NAF_CSV_FILE}"
    included_rows = []
    # FIXME: remplacer excluded_nafs par un set() et tester
    excluded_nafs = []
    with open(filename) as csvfile:
        reader = csv.DictReader(
            csvfile,
            delimiter=',',
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,
        )
        for row in reader:
            if row['rome'] in romes:
                included_rows.append(row)
            if include and row['rome'] in include:
                included_rows.append(row)
            if exclude and row['rome'] in exclude:
                excluded_nafs.append(row['naf'])

    included_rows[:] = [row for row in included_rows if row['naf'] not in excluded_nafs]
    logger.debug('raw naflist: %s', included_rows)

    out = {x['naf']: x['score'] for x in included_rows}

    return out, {}


def get_naf_sql(rules) -> str:
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


def parse_rome_size_prefs(rome_defs, tpe, pme, eti, ge) -> Iterable[bool]:
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


def sub_maxvg(vg, num):
    """
    Return the maximum obtained value, subfunction (see below)
    """
    if num >= int(vg):
        return '1'
    return str(int(vg) - num)
