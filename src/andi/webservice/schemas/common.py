"""
CLasses de base pour les modèles pydantic
"""
import typing as t
import uuid
from datetime import datetime

from pydantic import BaseModel, Field, PositiveInt

from ..hardsettings import API_VERSION
from ..library import utc_now


class MetaModel(BaseModel):
    """
    Métadonnées communes aux requêtes et réponses
    """
    v: PositiveInt = Field(..., alias='_v', description="Version")
    timestamp: datetime = Field(..., alias='_timestamp', description="Timestamp (UNIX Epoch)")
    query_id: uuid.UUID = Field(..., alias='_query_id', description="query UUID")
    session_id: t.Union[uuid.UUID, str] = Field("", alias='_session_id', description="browser session UUID")

    class Config:
        schema_extra = {
            "example": {
                "_v": API_VERSION,
                "_timestamp": str(utc_now()),
                "_query_id": str(uuid.uuid4()),
                "_session_id": str(uuid.uuid4())
            }
        }


def get_model_example(model: t.Type[BaseModel]) -> t.Dict[str, t.Any]:
    """Fournit l'exemple d'un modèle"""
    return model.Config.schema_extra["example"]
