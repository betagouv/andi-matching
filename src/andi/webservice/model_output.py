# pylint: skip-file
import uuid
from datetime import datetime
from enum import Enum
from typing import List, Union

from pydantic import BaseModel, Field, PositiveInt


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


class SizeTypes(str, Enum):
    tpe = 'tpe'
    pme = 'pme'
    eti = 'eti'
    ge = 'ge'


class Coordinates(BaseModel):
    lat: float
    lon: float


class Scoring(BaseModel):
    geo: int
    size: int
    contact: int
    pmsmp: int
    naf: int


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


class Model(BaseModel):
    """
    Modèle de validation des résultats de l'outil de matching
    """
    v: PositiveInt = Field(..., alias='_v', description="Version")
    timestamp: datetime = Field(..., alias='_timestamp', description="Timestamp (UNIX Epoch)")
    query_id: uuid.UUID = Field(..., alias='_query_id', description="query UUID")
    session_id: Union[uuid.UUID, str] = Field(..., alias='_session_id', description="browser session UUID")
    trace: str = Field(..., alias='_trace', description="Trace ID")
    data: List[ResponseData] = Field(..., description="response data")

    class Config:
        schema_extra = {
            'example': {
                "_v": 1,
                "_timestamp": "2019-11-18T10:14:14.758899+00:00",
                "_query_id": "efb7afcf-836b-4029-a3ce-f7c0b4b3499b",
                "_session_id": "efb7afcf-836b-4029-a3ce-f7c0b4b3499b",
                "_trace": "not_implemented_yet",
                "data": [{
                    "id": "29439",
                    "name": "REVILOX",
                    "address": "6 Rue de la Métairie, 95640 Marines, France",
                    "departement": "Val-d'Oise",
                    "phonenumber": "02345670",
                    "city": "Marines",
                    "coords": {
                        "lat": 93,
                        "lon": 18
                    },
                    "naf": "1623Z",
                    "siret": "32774533700029",
                    "distance": 5,
                    "scoring": {
                        "geo": 3,
                        "size": 5,
                        "contact": 1,
                        "pmsmp": 1,
                        "naf": 4
                    },
                    "score": 53,
                    "activity": "Fabrication de charpentes et d'autres menuiseries",
                    "size": "20-49"
                }]
            }}
