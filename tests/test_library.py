"""
Tests de andi.webservice.library
"""
import functools
import uuid

import andi.webservice.library as target
import pytest
from andi.webservice.schemas.match import DistanceCriterion, RomeCodesCriterion

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


@pytest.mark.asyncio
async def test_awaitable_blocking():
    def simple_blocking(param1, param2=2):
        return param1 + param2

    result = await target.awaitable_blocking(simple_blocking, 2)
    assert result == 4

    result = await target.awaitable_blocking(simple_blocking, 2, param2=5)
    assert result == 7

    # Avec functools.partial
    new_blocking = functools.partial(simple_blocking, 2, 8)
    result = await target.awaitable_blocking(new_blocking)
    assert result == 10

    # Avec une méthode de classe
    class Foo:
        def __init__(self, value):
            self.value = value

        def doit(self, value):
            return self.value + value

    f = Foo(5)
    result = await target.awaitable_blocking(f.doit, 5)
    assert result == 10
