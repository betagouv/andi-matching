# pylint: skip-file
"""
Rome returned by LaBonneBoite:
```json
   {
      "id":"K2401",
      "label":"Recherche en sciences de l'homme et de la soci\u00e9t\u00e9 (Philologue, ...)",
      "value":"Recherche en sciences de l'homme et de la soci\u00e9t\u00e9 (Philologue, ...)",
      "occupation":"recherche-en-sciences-de-l-homme-et-de-la-societe",
      "score":4.0
   }
```
"""
from typing import List

from pydantic import BaseModel, Field

from .common import MetaModel, get_schema_example


class InputModel(MetaModel):
    needle: str = Field(..., description="Search string")

    class Config:
        schema_extra = {
            "example": {
                **get_schema_example(MetaModel),
                "needle": "boulanger"
            }
        }


class RomeSuggestion(BaseModel):
    id: str
    label: str
    value: str
    occupation: str
    score: str

    class Config:
        schema_extra = {
            "example": {
                "id": "K1402",
                "label": "chirurgien-dentiste / chirurgienne-dentiste conseil",
                "value": "chirurgien-dentiste / chirurgienne-dentiste conseil",
                "occupation": "chirurgien-dentiste-chirurgienne-dentiste-conseil",
                "score": "11.56565858542299"
            }
        }


class Model(MetaModel):
    """
    Modèle des données sortantes de l'api suggestion code ROME
    Calqué sur l'API de La Bonne Boîte
    """
    data: List[RomeSuggestion] = Field([], description="List of rome suggestions")

    class Config:
        schema_extra = {
            "example": {
                **get_schema_example(MetaModel),
                "data": [{
                    **get_schema_example(RomeSuggestion)
                }]
            }
        }