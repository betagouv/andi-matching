import json
import logging
import string

import aiohttp
import pandas as pd
import unidecode

logger = logging.getLogger(__name__)


async def geo_code_query(query):
    """
    Query open geo-coding API from geo.api.gouv.fr
    Return spec: https://github.com/geocoders/geocodejson-spec
    """
    url = 'https://api-adresse.data.gouv.fr/search/'
    params = {
        'q': query,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            return await response.json()


def get_codes(data):
    # geo-coding standard does not respect lat / lon order
    lon, lat = data['features'][0]['geometry']['coordinates']
    return lat, lon


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
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            logger.debug('Querying LaBonneBoite...')
            response = await response.text()
            return json.loads(response)
            # FIXME: API response content-type is not json
            # return await response.json()


def normalize(txt):
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


def words_get(raw_query):
    query = normalize(raw_query)
    return query.split()


def result_build(rome, rome_label, rome_slug, ogr_label=None):
    if ogr_label:
        label = f"{rome_label} ({ogr_label}, ...)"
    else:
        label = rome_label
    return {
        'id': rome,
        'label': label,
        'value': label,
        'occupation': rome_slug,
        'score': 5
    }


def rome_suggest(query, rome_df, ogr_df):
    words = words_get(query)
    rome_raw_matches = []
    ogr_raw_matches = []
    for word in words:
        rome_raw_matches.append(rome_df[rome_df['stack'].str.contains(word)])
        ogr_raw_matches.append(ogr_df[ogr_df['stack'].str.contains(word)])
    rome_matches = pd.concat(rome_raw_matches)
    ogr_matches = pd.concat(ogr_raw_matches)

    results = {}
    for _i, rome_row in rome_matches.iterrows():
        results[rome_row['rome']] = result_build(
            rome_row['rome'],
            rome_row['label'],
            rome_row['slug']
        )

    for _i, ogr_row in ogr_matches.iterrows():
        rome = ogr_row['rome']
        ogr_romes = rome_df[rome_df['rome'] == rome]
        for _j, rome_row in ogr_romes.iterrows():
            results[rome] = result_build(
                rome,
                rome_row['label'],
                rome_row['slug'],
                ogr_row['label']
            )
    return list(results.values())
