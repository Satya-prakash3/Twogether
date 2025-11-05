import uuid
from fastapi import APIRouter

from app.core.jwt import (
    create_access_token, 
    create_refresh_token
)
from app.api.auth.services import (
    create_session
)


auth_router = APIRouter()


@auth_router.get("/token")
async def create_token():
    token = create_access_token(subject=12345, token_version=1)
    refresh = create_refresh_token(subject=12345, session_id=str(uuid.uuid4()))
    session = await create_session(user_id=123, jti="satr",refresh_token="asd", metadata={"hello":"hello"}, ttl=123)
    print(session)
    return {"token": token, "refresh": refresh}