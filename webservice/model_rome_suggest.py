import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel, Schema, PositiveInt

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


class InputModel(BaseModel):
    v: PositiveInt = Schema(..., alias='_v', description="Version")
    timestamp: datetime = Schema(..., alias='_timestamp', description="Timestamp (UNIX Epoch)")
    query_id: uuid.UUID = Schema(..., alias='_query_id', description="query UUID")
    session_id: uuid.UUID = Schema(..., alias='_session_id', description="browser session UUID")
    needle: str = Schema(..., description="Search string")


class RomeSuggestion(BaseModel):
    id: str
    label: str
    value: str
    occupation: str
    score: str


class Model(BaseModel):
    """
    Modèle des données sortantes de l'api suggestion code ROME
    Calqué sur l'API de La Bonne Boîte
    """
    v: PositiveInt = Schema(..., alias='_v', description="Version")
    timestamp: datetime = Schema(..., alias='_timestamp', description="Timestamp (UNIX Epoch)")
    query_id: uuid.UUID = Schema(..., alias='_query_id', description="query UUID")
    session_id: uuid.UUID = Schema(..., alias='_session_id', description="browser session UUID")
    data: List[RomeSuggestion] = Schema([], description="List of rome suggestions")
