import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.logging import (
    get_logger
)
from app.core.config import (
    env,
    globalSettings
)
from app.common.constants import Constants

logger = get_logger("app.main")

if env.app_env not in ["developement", "production"]:
    logger.error("")
    raise ValueError("Kindly provide a valid project environment.")


if env.app_env == "developement":
    app = FastAPI(
        title=Constants.APP_NAME, 
        version="0.1.0",
        docs_url="/api/v1/docs",
        redoc_url="/api/v1/redoc",
        openapi_url="/api/v1/oprnapi.json"
    )
else:
    app = FastAPI(
        title=Constants.APP_NAME, 
        version="0.1.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None
    )
    
app.mount("/static", StaticFiles(directory=globalSettings.STATIC_DIR), name="static")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join(globalSettings.STATIC_DIR, "favicon/favicon.ico"))

@app.get("/", include_in_schema=False)
def root():
    return {"message": "Welcome to Universal Video Downloader Backend. See /api/v1/hello"}

@app.get("/health", tags=["Health"])
async def health_check():
    logger.info("Health check requested")
    return {"status": "ok", "environment": env.app_env}



