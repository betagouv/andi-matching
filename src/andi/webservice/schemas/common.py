"""
CLasses de base pour les modèles pydantic
"""
import typing as t

from pydantic import BaseModel


def get_model_example(model: t.Type[BaseModel]) -> t.Dict[str, t.Any]:
    """Fournit l'exemple d'un modèle"""
    return model.Config.schema_extra["example"]
