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
    Modèle de validation des requêtes en entrée de l'outil de matching
    """
    v: PositiveInt = Schema(..., alias='_v', description="Version")
    timestamp: datetime = Schema(..., alias='_timestamp', description="Timestamp (UNIX Epoch)")
    query_id: uuid.UUID = Schema(..., alias='_query_id', description="query UUID")
    session_id: uuid.UUID = Schema(..., alias='_session_id', description="browser session UUID")
    address: Address = Schema(..., description="query base address")
    criteria: List[Criteria] = []
