import pytest

import library


"""
Expected geo api output:
{
    "type": "FeatureCollection",
    "version": "draft",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    2.331544,
                    48.849392
                ]
            },
            "properties": {
                "label": "8 Rue Honor\u00e9 Chevalier 75006 Paris",
                "score": 0.9640258493210577,
                "housenumber": "8",
                "id": "75106_4647_00008",
                "type": "housenumber",
                "name": "8 Rue Honor\u00e9 Chevalier",
                "postcode": "75006",
                "citycode": "75106",
                "x": 650946.7,
                "y": 6861246.38,
                "city": "Paris",
                "district": "Paris 6e Arrondissement",
                "context": "75, Paris, \u00cele-de-France",
                "importance": 0.6042843425316358,
                "street": "Rue Honor\u00e9 Chevalier"
            }
        }
    ],
    "attribution": "BAN",
    "licence": "ODbL 1.0",
    "query": "8 rue Honor\u00e9 Chevalier, Paris",
    "limit": 5
}
"""


@pytest.mark.asyncio
async def test_string_query():
    out = await library.geo_code_query("8 rue Honoré Chevalier, Paris")
    assert out is not None
    assert isinstance(out, dict)


@pytest.mark.asyncio
async def test_get_codes():
    out = await library.geo_code_query("8 rue Honoré Chevalier, Paris")
    lat, lon = library.get_codes(out)
    assert lat == 48.849392
    assert lon == 2.331544
