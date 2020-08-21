"""
Modèle des données en entrée pour le service matching

Prototype convenu:
```json
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
```
"""
import logging
# pylint: skip-file
from enum import Enum
from typing import List, Union, Tuple

from pydantic import BaseModel, Field, Json, PositiveInt

from .common import get_model_example
from ..library import geo_code_query

logger = logging.getLogger(__name__)


# Modèles pour la requête
# =======================

class AddressTypes(str, Enum):
    string = 'string'
    geoapigouv = 'geoapigouv'


class Address(BaseModel):
    type: AddressTypes = Field(..., description="AddressType")
    value: Union[str, Json] = None

    class Config:
        schema_extra = {
            "example": {
                "type": "string",
                "value": "12, rue François Bonvin - 75015 Paris"
            }
        }

    async def get_coord(self) -> Tuple[float, float]:
        if self.type == 'string':
            addr_string = self.value
            geo_data = await geo_code_query(addr_string)
        elif self.type == 'geoapigouv':
            geo_data = self.value
        else:
            logger.error(f"Unknown address type '{self.type}'.")
            raise
        lon, lat = geo_data['features'][0]['geometry']['coordinates']
        logger.debug('Extracted query coordinates lat %s lon %s', lat, lon)
        return lat, lon


class Criterion(BaseModel):
    priority: PositiveInt = Field(..., description="Priority (1 to 5) of the criterion")


class DistanceCriterion(Criterion):
    name: str = Field('distance', const=True, description="Name of criteria")
    distance_km: int

    class Config:
        schema_extra = {
            "example": {
                'priority': 2,
                'name': 'distance',
                'distance_km': 10
            }
        }


class RomeCode(BaseModel):
    id: str = Field('...', description="Rome ID")
    include: bool = Field(True, description="Include all NAF codes related to ROME")
    exclude: bool = Field(False, description="Exclude all NAF codes related to ROME")

    class Config:
        schema_extra = {
            "example": {
                "id": "A1202",
                "include": True,
                "exclude": False
            }
        }


class RomeCodesCriterion(Criterion):
    name: str = Field('rome_codes', const=True, description="Name of criteria")
    rome_list: List[RomeCode] = Field(..., description="List of rome codes")
    exclude_naf: list = Field([], description="List of naf codes to exclude")

    class Config:
        schema_extra = {
            "example": {
                'priority': 5,
                'name': 'rome_codes',
                'rome_list': [{**get_model_example(RomeCode)}],
                "exclude_naf": []
            }
        }


class EntreprisesQueryModel(BaseModel):
    """
    Modèle de validation des requêtes de l'outil de matching
    """
    address: Address = Field(..., description="query base address")
    criteria: List[Union[
        DistanceCriterion,
        RomeCodesCriterion,
    ]] = Field([], description="List of criteria")

    class Config:
        schema_extra = {
            'example': {
                'address': {
                    **get_model_example(Address)
                },
                'criteria': [
                    {
                        **get_model_example(DistanceCriterion)
                    },
                    {
                        **get_model_example(RomeCodesCriterion)
                    }
                ]
            }
        }


# Modèles pour la réponse
# =======================

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


class EntrepriseResponse(BaseModel):
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
                    **get_model_example(Coordinates)
                },
                "naf": "1623Z",
                "siret": "32774533700029",
                "distance": 5,
                "scoring": {
                    **get_model_example(Scoring)
                },
                "score": 53,
                "activity": "Fabrication de charpentes et d'autres menuiseries",
                "size": "20-49"
            }
        }
