from fastapi import APIRouter

from app.api.user.routers import user_router

api_main_router = APIRouter()


api_main_router.include_router(user_router, tags=['User APIs'])

