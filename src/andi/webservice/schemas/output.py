# pylint: skip-file
"""
Modèle des données en sortie pour le service matching

Prototype convenu:
```json
{
    '_v': 1,
    '_timestamp': 123125412,
    '_query_id': 'efb7afcf-836b-4029-a3ce-f7c0b4b3499b',
    '_session_id': 'efb7afcf-836b-4029-a3ce-f7c0b4b3499b',
    '_trace': 'aweofuiiu9274083',
    'data':
        [
            {
                'id': '12',
                'name': 'Pains d\'Amandine',
                'address': 'ADDRESSE',
                'departement': '29'
                'city': 'Cergy',
                'coords': {'lat': 93.123, 'lon': 83.451},
                'size': 'pme',
                'naf': '7711A',
                'siret': '21398102938',
                'distance': 54,
                'scoring': {'geo': 3, 'size': 4, 'contact': 2, 'pmsmp': 3, 'naf': 5},
                'score': 53,
                'activity': 'Boulangerie',
            },
        ]
}
```
"""
from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from .common import MetaModel, get_schema_example


class SizeTypes(str, Enum):
    tpe = 'tpe'
    pme = 'pme'
    eti = 'eti'
    ge = 'ge'


class Coordinates(BaseModel):
    lat: float
    lon: float

    class Config:
        schema_extra = {
            "example": {
                "lat": 21.656554,
                "lon": 55.323567
            }
        }


class Scoring(BaseModel):
    geo: int
    size: int
    contact: int
    pmsmp: int
    naf: int

    class Config:
        schema_extra = {
            "example": {
                "geo": 3,
                "size": 5,
                "contact": 1,
                "pmsmp": 1,
                "naf": 4
            }
        }


class ResponseData(BaseModel):
    id: str
    name: str
    address: str
    departement: str
    phonenumber: str = None
    city: str
    coords: Coordinates
    # FIXME: enum size type makes validator crash
    # size: SizeTypes = SizeTypes.pme
    size: str = None
    naf: str
    siret: str
    distance: float
    scoring: Scoring
    score: int
    activity: str

    class Config:
        schema_extra = {
            "example": {
                "id": "29439",
                "name": "REVILOX",
                "address": "6 Rue de la Métairie, 95640 Marines, France",
                "departement": "Val-d'Oise",
                "phonenumber": "02345670",
                "city": "Marines",
                "coords": {
                    **get_schema_example(Coordinates)
                },
                "naf": "1623Z",
                "siret": "32774533700029",
                "distance": 5,
                "scoring": {
                    **get_schema_example(Scoring)
                },
                "score": 53,
                "activity": "Fabrication de charpentes et d'autres menuiseries",
                "size": "20-49"
            }
        }


class Model(MetaModel):
    """
    Modèle de validation des résultats de l'outil de matching
    """
    trace: str = Field(..., alias='_trace', description="Trace ID")
    data: List[ResponseData] = Field(..., description="response data")

    class Config:
        schema_extra = {
            'example': {
                **get_schema_example(MetaModel),
                "_trace": "not_implemented_yet",
                "data": [{
                    **get_schema_example(ResponseData)
                }]
            }}
