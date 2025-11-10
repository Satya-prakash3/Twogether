from fastapi import APIRouter, Depends, Request, Response, Cookie, HTTPException, status
from typing import Optional

from app.api.auth.services import user_login, logout_current_session
from app.api.auth.schemas import (
    Login,
)
from app.core.config import env
from app.common.utils import success_response


auth_router = APIRouter()

REFRESH_COOKIE_NAME = "refresh_token"


@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login(response: Response, payload: Login, request: Request):

    meta_data = {
        "ip": request.client.host if request and request.client else None,
        "user_agent": request.headers.get("user-agent") if request else None,
    }

    result = await user_login(data=payload.model_dump(), metadata=meta_data)
    refresh_token = result.get("refresh_token")
    max_age = result.get("refresh_expires_in", env.refresh_token_expire_seconds)

    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=(env.app_env == "production"),
        samesite="lax",
        max_age=max_age,
        path="/" if env.app_env == "developement" else "/auth/refresh",
    )

    return success_response(
        message="Login successful",
        data={
            "access_token": result.get("access_token"),
            "expires_in": result.get("access_expires_in"),
        },
    )


@auth_router.post("/logout")
async def logout_from_current_session(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
):
    """
    Logout current session (uses refresh cookie).
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Refresh token missing"
        )

    await logout_current_session(refresh_token)

    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        path="/" if env.app_env == "developement" else "/auth/refresh",
    )
    return success_response("Logged out", data=None)
