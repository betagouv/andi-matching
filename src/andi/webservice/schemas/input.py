"""
Modèle des données en entrée pour le service matching
"""
import logging
# pylint: skip-file
from enum import Enum
from typing import List, Union, Tuple

from pydantic import BaseModel, Field, Json, PositiveInt

from .common import MetaModel, get_schema_example
from ..library import geo_code_query, get_codes

logger = logging.getLogger(__name__)


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
                "value": "5, rue de la Paix - 55320 Sacogne"
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
        lat, lon = get_codes(geo_data)
        logger.debug('Extracted query coordinates lat %s lon %s', lat, lon)
        return lat, lon


# FIXME: Semble inutilisé
class CriteriaNames(str, Enum):
    distance = 'distance'
    rome_codes = 'rome_codes'


class Criterion(BaseModel):
    priority: PositiveInt = Field(..., description="Priority (1 to 5) of the criterion")


class Criterion_Distance(Criterion):
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


class Criterion_RomeCodes(Criterion):
    name: str = Field('rome_codes', const=True, description="Name of criteria")
    rome_list: List[RomeCode] = Field(..., description="List of rome codes")
    exclude_naf: list = Field([], description="List of naf codes to exclude")

    class Config:
        schema_extra = {
            "example": {
                'priority': 5,
                'name': 'rome_codes',
                'rome_list': [{**get_schema_example(RomeCode)}],
                "exclude_naf": []
            }
        }


class Model(MetaModel):
    """
    Modèle de validation des requêtes de l'outil de matching
    """
    address: Address = Field(..., description="query base address")
    criteria: List[Union[
        Criterion_Distance,
        Criterion_RomeCodes,
    ]] = Field([], description="List of criteria")

    class Config:
        schema_extra = {
            'example': {
                **get_schema_example(MetaModel),
                'address': {
                    **get_schema_example(Address)
                },
                'criteria': [
                    {
                        **get_schema_example(Criterion_Distance)
                    },
                    {
                        **get_schema_example(Criterion_RomeCodes)
                    }
                ]
            }
        }
