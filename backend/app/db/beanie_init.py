from beanie import init_beanie

from app.db.mongo import mongo
from app.core.config import globalSettings
from app.core.logging import get_logger

logger = get_logger("app.db")


async def initialize_beanie():
    await init_beanie(
        database = mongo.db,
        document_models = globalSettings.BEANIE_MODELS
    )
    
