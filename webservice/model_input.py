import uuid
from datetime import datetime
from enum import Enum
from typing import List, Union

from pydantic import BaseModel, Json, PositiveInt, Schema


"""
Modèle des données en entrée pour le service matching
"""


class AddressTypes(str, Enum):
    string = 'string'
    geoapigouv = 'geoapigouv'


class Address(BaseModel):
    type: AddressTypes = Schema(..., description="AddressType")
    value: Union[str, Json] = None


class CriteriaNames(str, Enum):
    distance = 'distance'
    rome_codes = 'rome_codes'


class Criterion(BaseModel):
    priority: PositiveInt = Schema(..., description="Priority (1 to 5) of the criterion")


class Criterion_Distance(Criterion):
    name: str = Schema('distance', const=True, description="Name of criteria")
    distance_km: int


class RomeCode(BaseModel):
    id: str = Schema('...', description="Rome ID")
    include: bool = Schema(True, description="Include all NAF codes related to ROME")
    exclude: bool = Schema(False, description="Exclude all NAF codes related to ROME")


class Criterion_RomeCodes(Criterion):
    name: str = Schema('rome_codes', const=True, description="Name of criteria")
    rome_list: List[RomeCode] = Schema(..., description="List of rome codes")
    exclude_naf: list = Schema([], description="List of naf codes to exclude")


class Model(BaseModel):
    """
    Modèle de validation des requêtes de l'outil de matching
    """
    v: PositiveInt = Schema(..., alias='_v', description="Version")
    timestamp: datetime = Schema(..., alias='_timestamp', description="Timestamp (UNIX Epoch)")
    query_id: uuid.UUID = Schema(..., alias='_query_id', description="query UUID")
    session_id: uuid.UUID = Schema(..., alias='_session_id', description="browser session UUID")
    address: Address = Schema(..., description="query base address")
    criteria: List[Union[
        Criterion_Distance,
        Criterion_RomeCodes,
    ]] = Schema([], description="List of criteria")

    class Config:
        schema_extra = {
            'example': {
                '_v': 1,
                '_timestamp': 1239120938,
                '_query_id': 'efb7afcf-836b-4029-a3ce-f7c0b4b3499b',
                '_session_id': 'efb7afcf-836b-4029-a3ce-f7c0b4b3499b',
                'address': {
                    'type': 'string',
                    'value': '16 Rue le Clos du Puits, 95830 Cormeilles-en-Vexin'
                },
                'criteria': [
                    {
                        'priority': 2,
                        'name': 'distance',
                        'distance_km': 10
                    },
                    {
                        'priority': 5,
                        'name': 'rome_codes',
                        'rome_list': [{'id': 'M1805', 'include': True}]
                    }
                ]
            }}
