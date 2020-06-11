# pylint: skip-file
import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, PositiveInt


class InputModel(BaseModel):
    """
    Modèle données entrantes endpoint employeur
    """
    v: PositiveInt = Field(..., alias='_v', description="Version")
    timestamp: datetime = Field(..., alias='_timestamp', description="Timestamp (UNIX Epoch)")
    query_id: uuid.UUID = Field(..., alias='_query_id', description="query UUID")
    session_id: uuid.UUID = Field(..., alias='_session_id', description="browser session UUID")
    siret: str = Field(..., description="Siret")

    class Config:
        schema_extra = {
            'example': {
                '_v': 1,
                '_timestamp': 1239120938,
                '_query_id': 'efb7afcf-836b-4029-a3ce-f7c0b4b3499b',
                '_session_id': 'efb7afcf-836b-4029-a3ce-f7c0b4b3499b',
                'siret': '18002002600019'
            }
        }


class EmployerData(BaseModel):
    siret: str
    name: str
    lat: float
    lon: float
    sector: str
    naf: str
    size: str
    street_address: str
    flags: List[str]


class Model(BaseModel):
    """
    Modèle données sortantes endpoint employeur
    """
    v: PositiveInt = Field(..., alias='_v', description="Version")
    timestamp: datetime = Field(..., alias='_timestamp', description="Timestamp (UNIX Epoch)")
    query_id: uuid.UUID = Field(..., alias='_query_id', description="query UUID")
    session_id: uuid.UUID = Field(..., alias='_session_id', description="browser session UUID")
    data: EmployerData = Field(..., description="Enterprise data")
