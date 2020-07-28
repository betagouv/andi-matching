"""
Tests de andi.webservice.library
"""
import andi.webservice.library as library
import pytest
from andi.webservice.schemas.match import DistanceCriterion, RomeCodesCriterion

from .conftest import skip_connected

@skip_connected
@pytest.mark.asyncio
async def test_string_query():
    out = await library.geo_code_query("8 rue Honoré Chevalier, Paris")
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
    result = library.get_parameters(criteria)
    assert result == {'includes': [], 'excludes': [], 'sizes': ['pme'],
                      'multipliers': {'fg': 2, 'fn': 5, 'ft': 2, 'fw': 4, 'fc': 3}, 'romes': ['A1202'],
                      'max_distance': 15}
