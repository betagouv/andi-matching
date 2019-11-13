from datetime import datetime
from enum import Enum
import uuid
from typing import List, Union
from pydantic import (
    BaseModel,
    PositiveInt,
    Json,
    Schema,
)

"""
Modèle des données en entrée pour le service matching

Prototype convenu:
```json
{
    '_v': 1,
    '_timestamp': 1239120938,
    '_query_id': 'efb7afcf-836b-4029-a3ce-f7c0b4b3499b',
    '_session_id': 'efb7afcf-836b-4029-a3ce-f7c0b4b3499b',
    'address': {
        'type': 'string|geoapigouv'
        'content': '',
    },
    'criteria': [
        {
            'id': 'distance',
            'value': 10,
            'priority': 5,
        },
        {
            'id': 'rome_codes',
            'value':[ { 'code': 'M1805', 'priority': 3 } ],
            'priority': 5,
            ]
        },
    ]
}
```
"""


class AddressTypes(str, Enum):
    string = 'string'
    geoapigouv = 'geoapigouv'


class Address(BaseModel):
    type: AddressTypes = Schema(..., description="AddressType")
    value: Union[str, Json] = None


class CriteriaTypes(str, Enum):
    distance = 'distance'
    rome_codes = 'rome_codes'


class Criteria(BaseModel):
    type: CriteriaTypes = Schema(..., description="Type")
    value: Union[str, list, Json] = None
    priority: PositiveInt = Schema(..., gt=0, lt=5, description="Priority (1 to 5)")


class Model(BaseModel):
    """
    Modèle de validation des requêtes de l'outil de matching
    """
    v: PositiveInt = Schema(..., alias='_v', description="Version")
    timestamp: datetime = Schema(..., alias='_timestamp', description="Timestamp (UNIX Epoch)")
    query_id: uuid.UUID = Schema(..., alias='_query_id', description="query UUID")
    session_id: uuid.UUID = Schema(..., alias='_session_id', description="browser session UUID")
    address: Address = Schema(..., description="query base address")
    criteria: List[Criteria] = Schema([], description="List of criteria")
