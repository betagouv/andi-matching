import uuid
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, Json, PositiveInt, IPvAnyAddress
"""
Data points:
------------
version
timestamp
order

session_id
page
action (enum)
meta

client context
    - referer
    - url

server context
    - client ip
    - user agent
    - reception_timestamp
---
"""


class page(str, Enum):
    landing_page = 'landing_page'
    cgu = 'cgu'
    pasapas = 'pasapas'
    quest_match = 'quest_match'
    result_match = 'result_match'


class Actions(str, Enum):
    arrival = 'arrival'  # L'utilisateur arrive sur la page
    depart = 'departure'  # L'utilisateur quitte la page (meta: vers ou ?)
    mailto = 'mailto'  # L'utilisateur utilise un mailto (meta: vers quoi ?)
    linkto = 'linkto'  # L'utilisateur clique sur un lien et quitte la page (meta: vers ou ?)
    bilan = 'bilan'  # L'utilisateur arrive au bilan (meta: résultats)
    to_matching = 'to_matching'  # L'utilisateur continue vers matching
    question_arrival = 'question_arrival'  # L'utilisateur arrive sur une question (meta: laquelle)
    question_departure = 'question_departure'  # L'utilisateur part d'une question (meta: laquelle)
    question_response = 'question_response'  # L'utilisateur répond à une question (meta: quelle question / quelle réponse)
    matching_search = 'matching_search'  # L'utilisateur effectue une recherche (meta: critères)
    matching_results = 'matching_results'  # L'utilisateur reçoit les résultats (meta: combien)
    matching_error = 'matching_error'  # L'utilisateur reçoit une erreur lors de son utilisation du service matching (meta: message d'erreur)
    more_results = 'more_results'  # L'utilisateur veut afficher plus de résultats
    result_click = 'result_click'  # L'utilisateur clique sur un résultat (meta: vers ou ?)
    guidance_click = 'guidance_click'  # L'utilisateur clique sur les conseils de contact


class ClientContext(BaseModel):
    referer: str = None


class ServerContext(BaseModel):
    client_ip: IPvAnyAddress = None
    reception_timestamp: datetime = Field(None, alias='_timestamp', description="Timestamp (UNIX Epoch)")
    origin: str = None
    user_agent: str = None


class Model(BaseModel):
    """
    Modèle validation tracker ANDi
    """
    v: PositiveInt = Field(..., alias='_v', description="Version")
    timestamp: datetime = Field(..., description="Timestamp (UNIX Epoch)")
    order: int

    session_id: uuid.UUID = Field(..., description="browser session UUID")
    page: str = None
    action: Actions = Field(..., description="Type d'action")
    meta: Json = None

    client_context: ClientContext
    server_context: ServerContext

    class Config:
        schema_extra = {
            'example': {
                "_v": 1,
                "timestamp": "2019-11-18T10:14:14.758899+00:00",
                "order": 10,
                "session_id": "77777777-6666-5555-4444-333333333333",
                "page": "test_page",
                "action": "arrival",
                "meta": {},
                "client_context": {
                    "referer": None,
                },
                "server_context": {
                    "user_agent": "DOES_NOT_EXIST",
                    "client_ip": None,
                    "reception_timestamp": None,
                    "referer": "http://example.com"
                }
            }
        }
