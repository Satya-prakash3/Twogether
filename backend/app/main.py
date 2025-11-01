import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import HTTPException


from app.common.constants import Constants
from app.common.exception import (
    InvalidEnvironmentError,
    BaseException,
    app_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
)
from app.core.logging import (
    get_logger
)
from app.core.config import (
    env,
    globalSettings
)
from app.db.mongo import (
    connect_to_mongo,
    close_mongo_connection
)
from app.common.utils import (
    utils_router
)


#=====================================APPLICATION_LOGIC_STARTS=====================================

logger = get_logger("app.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    print("MongoDB Connected")
    yield

    await close_mongo_connection()
    print("MongoDB Connection Closed")

if env.app_env not in ["developement", "production"]:
    logger.error("Invalid Environment provided")
    raise InvalidEnvironmentError("Kindly provide a valid project environment.")


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
app.add_exception_handler(BaseException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(router=utils_router, prefix="/api/v1")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join(globalSettings.STATIC_DIR, "favicon/favicon.ico"))


@app.get("/", include_in_schema=False)
def root():
    return {"message": "Welcome to Universal Video Downloader Backend. See /api/v1/health"}


@app.get("/ping")
async def ping():
    logger.info("Ping endpoint hit", extra={"extra": {"service": "api", "user": "test_user"}})
    return {"message": "pong"}