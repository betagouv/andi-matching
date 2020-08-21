import json

import andi.webservice.schemas.entreprises as target
import pytest

from .conftest import skip_connected


@pytest.mark.asyncio
async def test_address_model_mocked(mocker, mocked_aiohttp_response):
    input = {
        "type": "string",
        "value": "15 rue du Four - 75006 Paris"
    }
    # https://api-adresse.data.gouv.fr/search/?q=15%20rue%20du%20Four%20-%2075006%20Paris
    output = {
        'type': 'FeatureCollection', 'version': 'draft', 'features': [
            {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [2.334873, 48.852733]},
             'properties': {'label': '15 Rue du Four 75006 Paris', 'score': 0.9555176576078688, 'housenumber': '15',
                            'id': '75106_3763_00015', 'type': 'housenumber', 'x': 651194.12, 'y': 6861615.81,
                            'importance': 0.5106942336865562, 'name': '15 Rue du Four', 'postcode': '75006',
                            'citycode': '75106', 'city': 'Paris', 'district': 'Paris 6e Arrondissement',
                            'context': '75, Paris, Île-de-France', 'street': 'Rue du Four'}}], 'attribution': 'BAN',
        'licence': 'ETALAB-2.0', 'query': '15 rue du Four - 75006 Paris', 'limit': 5
    }
    fake_response = mocked_aiohttp_response(json.dumps(output), 200)
    mocker.patch("aiohttp.ClientSession.get", return_value=fake_response)
    addr = target.Address.parse_obj(input)
    lat, lon = await addr.get_coord()
    assert abs(lat - 48.852733) < 0.1
    assert abs(lon - 2.334873) < 0.1


@skip_connected
@pytest.mark.asyncio
async def test_address_model_real():
    """Le même que ci-dessus mais en utilisant l'API externe réelle"""
    input = {
        "type": "string",
        "value": "15 rue du Four - 75006 Paris"
    }
    addr = target.Address.parse_obj(input)
    lat, lon = await addr.get_coord()
    assert abs(lat - 48.852733) < 0.1
    assert abs(lon - 2.334873) < 0.1
