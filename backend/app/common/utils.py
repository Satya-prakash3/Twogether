from fastapi import APIRouter
from app.core.config import env
from app.core.logging import get_logger

utils_router = APIRouter()



logger = get_logger("app.common.utils")

@utils_router.get("/health", tags=["Health"])
async def health_check():
    logger.info("Health check requested")
    return {"status": "ok", "environment": env.app_env}

@utils_router.get("/hello", tags=["Hello"])
async def hello():
    logger.info("Hello API called.", extra={"extra": {"service": "api", "user": "test_user"}})
    return {"status":"Hello"}
