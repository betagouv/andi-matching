import logging
from typing import List

from asgiref.sync import sync_to_async
from fastapi import APIRouter

from ..romes import SUGGEST_STATE, match as rome_suggest
from ..schemas.romes import RomesQueryModel, RomeSuggestion
from ..settings import config

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/romes", response_model=List[RomeSuggestion],
            operation_id="rechercherROMEs",
            summary="Suggestions ROME",
            description="Suggère des codes ROME et métiers en fonction d'un pattern de nom de métier")
async def api_rome_suggest(q: str = ""):
    """
    Rome suggestion endpoint:
    Query rome code suggestions according to input string,
    only returning top 15 results.
    """
    logger.debug('received query %s', [q])
    query = RomesQueryModel(needle=q)

    rome_list = await sync_to_async(rome_suggest)(query.needle, SUGGEST_STATE)
    logger.debug('Obtained %s results', len(rome_list))
    return rome_list[:config.ROME_SUGGEST_LIMIT]
