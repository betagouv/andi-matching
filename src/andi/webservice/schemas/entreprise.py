from typing import List
from pydantic import BaseModel, Field
from .common import MetaModel, get_schema_example


class InputModel(MetaModel):
    siret: str = Field(..., description="Siret")

    class Config:
        schema_extra = {
            "example": {
                **get_schema_example(MetaModel),
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

    class Config:
        schema_extra = {
            "example": {
                "siret": "362 521 879 00034",
                "name": "La pantoufle Française",
                "lat": 41.40338,
                "lon": 2.17403,
                "sector": "Fabrication de chaussures",
                "naf": "1520Z",
                "size": "pme",
                "street_address": "155, boulevard de la Pompe - 14000 Grolle",
                "flags": []
            }
        }


class Model(MetaModel):
    data: EmployerData = Field(..., description="Enterprise data")

    class Config:
        schema_extra = {
            "example": {
                **get_schema_example(MetaModel),
                "data": {**get_schema_example(EmployerData)}
            }
        }
