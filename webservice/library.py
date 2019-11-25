import aiohttp
import json
import logging

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
