"""
Tests de andi.webservice.library
"""
import uuid

import andi.webservice.library as target
import pytest
from andi.webservice.schemas.entreprises import DistanceCriterion, RomeCodesCriterion

from .conftest import skip_connected


@skip_connected
@pytest.mark.asyncio
async def test_string_query():
    out = await target.geo_code_query("8 rue Honoré Chevalier, Paris")
    assert out is not None
    assert isinstance(out, dict)


def test_get_parameters():
    criteria = [
        RomeCodesCriterion.parse_obj({
            "priority": 5,
            "name": "rome_codes",
            "rome_list": [
                {
                    "id": "A1202",
                    "include": True,
                    "exclude": False
                },
                {
                    "id": "A1111",
                    "include": False,
                    "exclude": False
                }

            ],
            "exclude_naf": []
        }),
        DistanceCriterion.parse_obj({
            "priority": 2,
            "name": "distance",
            "distance_km": 15
        })
    ]
    result = target.get_parameters(criteria)
    assert result == {'includes': [], 'excludes': [], 'sizes': ['pme'],
                      'multipliers': {'fg': 2, 'fn': 5, 'ft': 2, 'fw': 4, 'fc': 3}, 'romes': ['A1202'],
                      'max_distance': 15}


def test_normalize():
    text = "Quelques mots  ont été normalizés."
    expected = "quelques mots ont ete normalizes"
    assert target.normalize(text) == expected


def test_is_valid_uuid():
    # N'est pas un UUID
    assert not target.is_valid_uuid("5678")

    # Est un UUID valide
    assert target.is_valid_uuid(str(uuid.uuid4()))


def test_sync_g(client, app):
    @app.get("/1.0/schtroumpf")
    def schtroumpf():
        return target.g().api_version_info

    response = client.get("/1.0/schtroumpf")
    assert response.status_code == 200
    assert response.json() == [1, 0]


def test_async_g(client, app):
    @app.get("/1.0/schtroumpf")
    async def schtroumpf():
        return target.g().api_version_info

    response = client.get("/1.0/schtroumpf")
    assert response.status_code == 200
    assert response.json() == [1, 0]


def test_noversion_g(client, app):
    @app.get("/schtroumpf")
    def schtroumpf():
        plouf()
        return {"a": target.g().api_version_info, "b": target.g().value}

    def plouf():
        target.g().value = 10

    response = client.get("/schtroumpf")
    assert response.status_code == 200
    result = response.json()
    assert result["a"] is None
    assert result["b"] == 10
