from fastapi import APIRouter

from app.api.user.routers import user_router
from app.api.auth.routers import auth_router

api_main_router = APIRouter()

api_main_router.include_router(user_router, prefix="/user", tags=["User APIs"])
api_main_router.include_router(auth_router, prefix="/auth", tags=["Auth APIs"])
