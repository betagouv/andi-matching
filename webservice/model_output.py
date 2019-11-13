from datetime import datetime
from enum import Enum
import uuid
from typing import List
from pydantic import (
    BaseModel,
    PositiveInt,
    Schema,
)

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
    city: str
    coords: Coordinates
    size: SizeTypes
    naf: str
    siret: str
    distance: int
    scoring: Scoring
    score: int
    activity: str


class Model(BaseModel):
    """
    Modèle de validation des résultats de l'outil de matching
    """
    v: PositiveInt = Schema(..., alias='_v', description="Version")
    timestamp: datetime = Schema(..., alias='_timestamp', description="Timestamp (UNIX Epoch)")
    query_id: uuid.UUID = Schema(..., alias='_query_id', description="query UUID")
    session_id: uuid.UUID = Schema(..., alias='_session_id', description="browser session UUID")
    trace: str = Schema(..., alias='_trace', description="Trace ID")
    data = List[ResponseData] = Schema(..., description="response data")
