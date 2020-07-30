"""
Utilitaires divers et inclassables de l'appli
"""
from __future__ import annotations

import asyncio
import concurrent.futures
import datetime
import functools
import logging
import string
import typing
import uuid

import aiohttp
import pytz
import unidecode

if typing.TYPE_CHECKING:
    from .schemas.match import DistanceCriterion, RomeCodesCriterion
    from .schemas.common import MetaModel
    from typing import List, Union

from .hardconfig import AWAITABLE_BLOCKING_POOL_MAX_THREADS

logger = logging.getLogger(__name__)


async def geo_code_query(query: str) -> dict:
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


def parse_param(accumulator, criterion: Union[DistanceCriterion, RomeCodesCriterion]):
    res = getattr(CriterionParser, criterion.name)(criterion, accumulator)
    return res


def get_parameters(criteria: List[Union[DistanceCriterion, RomeCodesCriterion]]) \
        -> dict:
    """
    Construction des critères de recherche d'emploi pour la requête
    Args:
        criteria: Liste de critères ROME et distance (généralement deux)

    Returns:
        Dictionnaire de paramètres
    """
    return functools.reduce(parse_param, criteria, DEFAULT_MATCHING_PARAMS)


def normalize(text: str, minimum_size=3) -> str:
    """
    Generic standaridzed text normalizing function
    Args:
        text: Unicode text to be normalized
        minimum_size: discard words below this size
    Returns:
        normalized text
    Examples:
        >>> normalize("le TexTe  Présenté")
        'texte presente'
    """
    # Remove punctuation
    table = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    text = text.translate(table)

    # Lowercase
    text = text.lower()

    # Remove short letter groups
    text = text.split()
    text = [t for t in text if len(t) >= minimum_size]
    text = ' '.join(text)

    # Accent folding
    text = unidecode.unidecode(text)
    return text


def words_get(raw_query: str) -> List[str]:
    if not raw_query:
        return []
    query = normalize(raw_query)
    return query.split()


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


def get_trace_obj(query: MetaModel) -> t.Dict[str, t.Any]:
    return {
        '_query_id': query.query_id,
        '_session_id': query.session_id,
        '_trace': 'not_implemented_yet',
    }


# Running a blocking callable inside a coroutine
# ==============================================

# Use the better suited pool (see doc of ``concurrent.future```)

_awaitable_blocking_pool = concurrent.futures.ThreadPoolExecutor(
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
    result = await loop.run_in_executor(_awaitable_blocking_pool, new_func)
    return result
