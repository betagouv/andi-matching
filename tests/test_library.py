import json
import os
import pathlib

import pandas as pd
import pytest

import andi.webservice
import andi.webservice.library as library

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


@pytest.mark.asyncio
async def test_get_rome_suggestions():
    out = await library.rome_list_query("phil")
    print(json.dumps(out, indent=2))
    assert out is not None
    assert len(out) == 4
    found = False
    for res in out:
        if res.get('id') == 'K2401':
            found = True
    assert found


def test_get_rome_suggest():
    referentiels_dir = pathlib.Path(andi.webservice.__file__).resolve().parent / "referentiels"
    ROME_DF = pd.read_csv(referentiels_dir / "rome_lbb.csv")
    ROME_DF.columns = ['rome', 'rome_1', 'rome_2', 'rome_3', 'label', 'slug']
    OGR_DF = pd.read_csv(referentiels_dir / "ogr_lbb.csv")
    OGR_DF.columns = ['code', 'rome_1', 'rome_2', 'rome_3', 'label', 'rome']
    ROME_DF['stack'] = ROME_DF.apply(lambda x: library.normalize(x['label']), axis=1)
    OGR_DF['stack'] = OGR_DF.apply(lambda x: library.normalize(x['label']), axis=1)

    out = library.rome_suggest_v1("phil", (ROME_DF, OGR_DF))
    print(json.dumps(out, indent=2))
    assert out is not None
    assert len(out) == 4
    found = False
    for res in out:
        if res.get('id') == 'K2401':
            found = True
    assert found
