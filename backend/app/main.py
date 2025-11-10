import os
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.exceptions import HTTPException, RequestValidationError


from app.db.beanie_init import initialize_beanie
from app.common.constants import Constants
from app.core.redis import connect_to_redis, close_redis_connection
from app.common.exception import (
    InvalidEnvironmentError,
    BaseException,
    app_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.logging import get_logger
from app.core.config import env, globalSettings
from app.db.mongo import connect_to_mongo, close_mongo_connection

from app.common.api import common_api_router
from app.api.main import api_main_router


# =====================================APPLICATION_LOGIC_STARTS=====================================

logger = get_logger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    await initialize_beanie()
    await connect_to_redis()
    yield

    await close_mongo_connection()
    await close_redis_connection()


if env.app_env not in ["developement", "production"]:
    logger.error("Invalid Environment provided")
    raise InvalidEnvironmentError("Kindly provide a valid project environment.")


if env.app_env == "developement":
    app = FastAPI(
        title=Constants.APP_NAME,
        version="0.1.0",
        docs_url="/api/v1/document",
        redoc_url="/api/v1/redocument",
        openapi_url="/api/v1/openapiv1.json",
        lifespan=lifespan,
        swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    )
else:
    app = FastAPI(
        title=Constants.APP_NAME,
        version="0.1.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
        swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    )

app.mount("/static", StaticFiles(directory=globalSettings.STATIC_DIR), name="static")
templates = Jinja2Templates(directory="app/static/templates")

app.add_exception_handler(BaseException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(router=common_api_router, prefix=Constants.API_V1_URL)
app.include_router(router=api_main_router, prefix=Constants.API_V1_URL)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join(globalSettings.STATIC_DIR, "favicon/favicon.ico"))


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
