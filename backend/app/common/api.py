from fastapi import APIRouter
from app.core.config import env
from app.core.logging import get_logger

common_api_router = APIRouter()



logger = get_logger("app.common.utils")

@common_api_router.get("/health", tags=["Health"])
async def health_check():
    logger.info("Health check requested")
    return {"status": "ok", "environment": env.app_env}

