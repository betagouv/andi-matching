"""
Utilitaires divers et inclassables de l'appli
"""
from __future__ import annotations

import asyncio
import concurrent.futures
import datetime
import functools
import json
import logging
import os
import re
import string
import typing as t
import uuid

import aiohttp
import pandas as pd
import pytz
import unidecode
from fuzzywuzzy import fuzz
from pydantic import BaseModel

if t.TYPE_CHECKING:
    from .schemas.match import DistanceCriterion, RomeCodesCriterion

from .hardconfig import AWAITABLE_BLOCKING_POOL_MAX_THREADS

logger = logging.getLogger(__name__)


# ############################# Geo-coding functions
# ##################################################
async def geo_code_query(query):
    """
    Query open geo-coding API from geo.api.gouv.fr
    Return spec: https://github.com/geocoders/geocodejson-spec
    """
    url = 'https://api-adresse.data.gouv.fr/search/'
    params = {
        'q': query,
    }
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(url, params=params) as response:
            return await response.json()


# TODO: move to schemas/input
def get_coordinates(data):
    # geo-coding standard does not respect lat / lon order
    lon, lat = data['features'][0]['geometry']['coordinates']
    return lat, lon


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


class CriterionParser:
    @staticmethod
    def distance(criterion: DistanceCriterion, acc):
        acc['max_distance'] = criterion.distance_km
        acc['multipliers']['fg'] = criterion.priority
        return acc

    @staticmethod
    def rome_codes(criterion: RomeCodesCriterion, acc):
        # FIXME add rome include / exclude rule
        rome_codes = [rome.id for rome in criterion.rome_list if rome.include]
        acc['romes'] = rome_codes
        acc['multipliers']['fn'] = criterion.priority
        return acc


def parse_param(accumulator, criterion: t.Union[DistanceCriterion, RomeCodesCriterion]):
    res = getattr(CriterionParser, criterion.name)(criterion, accumulator)
    return res


def get_parameters(criteria: t.List[t.Union[DistanceCriterion, RomeCodesCriterion]]):
    return functools.reduce(parse_param, criteria, DEFAULT_MATCHING_PARAMS)


# FIXME: Obsolète
async def rome_list_query(query):
    """
    DEPRECATED
    Query rome suggestion API from labonneboite
    Example URL: https://labonneboite.pole-emploi.fr/suggest_job_labels?term=phil
    """
    url = 'https://labonneboite.pole-emploi.fr/suggest_job_labels'
    params = {
        'term': query,
    }
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(url, params=params) as response:
            logger.debug('Querying LaBonneBoite...')
            response = await response.text()
            return json.loads(response)
            # FIXME: API response content-type is not json
            # return await response.json()


# ##################### Rome suggesting functions V1
# ##################################################
# OBSOLETE
# See lib_rome_suggest_v2
def get_dataframes_v1():
    logger.info('Compiling dataframe references')
    current_dir = os.path.dirname(os.path.abspath(__file__))
    rome_df = pd.read_csv(f'{current_dir}/referentiels/rome_lbb.csv')
    rome_df.columns = ['rome', 'rome_1', 'rome_2', 'rome_3', 'label', 'slug']
    ogr_df = pd.read_csv(f'{current_dir}/referentiels/ogr_lbb.csv')
    ogr_df.columns = ['code', 'rome_1', 'rome_2', 'rome_3', 'label', 'rome']
    rome_df['stack'] = rome_df.apply(lambda x: normalize(x['label']), axis=1)
    ogr_df['stack'] = ogr_df.apply(lambda x: normalize(x['label']), axis=1)
    logger.info('Dataframe compilation done')
    return (rome_df, ogr_df)


# FIXME: Obsolète
def score_build(query, match):
    """
    Return matching score used to order search results
    fuzzywuzzy ratio calculates score on 100: we reduce that to 5 with 1 decimal
    """
    ratio = fuzz.ratio(query, match)
    return round(ratio / 20, 1)


# FIXME: Obsolète
def normalize(txt):
    """
    Generic standaridzed text normalizing function
    """
    # Remove punctuation
    table = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    txt = txt.translate(table)

    # Lowercase
    txt = txt.lower()

    # Remove short letter groups
    txt = txt.split()
    txt = [t for t in txt if len(t) >= 3]
    txt = ' '.join(txt)

    # Accent folding
    txt = unidecode.unidecode(txt)

    return txt


# FIXME: Obsolète
def words_get(raw_query):
    if not raw_query:
        return []
    query = normalize(raw_query)
    return query.split()


# FIXME: Obsolète
def result_build(score, rome, rome_label, rome_slug, ogr_label=None):
    if ogr_label:
        label = f"{rome_label} ({ogr_label}, ...)"
    else:
        label = rome_label

    return {
        'id': rome,
        'label': label,
        'value': label,
        'occupation': rome_slug,
        'score': score
    }


# FIXME: Obsolète, plus utilisé
def rome_suggest_v1(query, state):
    rome_df, ogr_df = state
    results = {}

    # Unelegant solution to uncontroled queries
    needle = normalize(re.sub(r'\([^\)]*\)', '', query).strip())

    check = rome_df[rome_df['stack'] == needle]
    if not check.empty:
        # Full title match, only one result possible
        results[check.iloc[0]['rome']] = result_build(
            100,
            check.iloc[0]['rome'],
            check.iloc[0]['label'],
            check.iloc[0]['slug']
        )
        return list(results.values())

    check = rome_df[rome_df['stack'].str.contains(needle)]
    if not check.empty:
        results[check.iloc[0]['rome']] = result_build(
            score_build(needle, check.iloc[0]['stack']),
            check.iloc[0]['rome'],
            check.iloc[0]['label'],
            check.iloc[0]['slug']
        )

    words = words_get(query)
    if len(words) == 0:
        return []
    rome_raw_matches = []
    ogr_raw_matches = []
    # Only using first 5 words
    for word in words[:5]:
        rome_raw_matches.append(rome_df[rome_df['stack'].str.contains(word)])
        ogr_raw_matches.append(ogr_df[ogr_df['stack'].str.contains(word)])
    rome_matches = pd.concat(rome_raw_matches)
    ogr_matches = pd.concat(ogr_raw_matches)

    for _i, ogr_row in ogr_matches.iterrows():
        rome = ogr_row['rome']
        ogr_romes = rome_df[rome_df['rome'] == rome]
        for _j, rome_row in ogr_romes.iterrows():
            results[rome] = result_build(
                score_build(query, ogr_row['stack']),
                rome,
                rome_row['label'],
                rome_row['slug'],
                ogr_row['label']
            )

    for _i, rome_row in rome_matches.iterrows():
        results[rome_row['rome']] = result_build(
            score_build(query, rome_row['stack']),
            rome_row['rome'],
            rome_row['label'],
            rome_row['slug']
        )
    return sorted(list(results.values()), key=lambda e: e['score'], reverse=True)


def utc_now() -> datetime.datetime:
    """
    Returns:
        Maintenant en UTC
    """
    return datetime.datetime.now(tz=pytz.utc)


def is_valid_uuid(val: t.AnyStr):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def get_trace_obj(query: BaseModel) -> t.Dict[str, t.Any]:
    return {
        '_query_id': query.query_id,
        '_session_id': query.session_id,
        '_trace': 'not_implemented_yet',
    }


# Running a blocking callable inside a coroutine
# ==============================================

# Use the better suited pool (see doc of ``concurrent.future```)

awaitable_blocking_pool = concurrent.futures.ThreadPoolExecutor(
    max_workers=AWAITABLE_BLOCKING_POOL_MAX_THREADS
)


# awaitable_blocking_pool = concurrent.futures.ProcessPoolExecutor()
# awaitable_blocking_pool = None  # Default asyncio pool


async def awaitable_blocking(func: t.Callable, *args: t.Any, **kwargs: t.Any) -> t.Any:
    """
    Enable to "await" a blocking I/O callable from an asyncio coroutine

    Args:
        func: The regular blocking callable (function, method)
        args: Positional arguments transmitted to ``func``
        kwargs: Keyword arguments transmitted to ``func``

    Returns:
        Anything that's returned by ``func``
    """
    loop = asyncio.get_running_loop()
    new_func = functools.partial(func, *args, **kwargs)
    result = await loop.run_in_executor(awaitable_blocking_pool, new_func)
    return result
