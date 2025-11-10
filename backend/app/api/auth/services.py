import json
import uuid
from typing import Optional, Any
from fastapi import HTTPException, status
from beanie.odm.operators.find.logical import Or
from datetime import datetime, timezone, timedelta


from app.core.jwt import create_access_token, create_refresh_token, verify_token
from app.core.config import env
from app.api.user.models import User
from app.core.redis import redis_client
from app.core.logging import get_logger
from app.common.services import BaseRepository
from app.common.security import verify_password

logger = get_logger("app.api.auth.service")

SESSION_PREFIX = "session"
BLACKLIST_PREFIX = "blacklist"

REFRESH_TOKEN_TTL = 30 * 24 * 60 * 60
BLACKLIST_TTL = 15 * 60


async def create_session(
    user_id: str,
    jti: str,
    refresh_token: str,
    metadata: dict | None = None,
    ttl: int = REFRESH_TOKEN_TTL,
) -> bool:
    """
    Create a new user session in Redis.

    Args:
        user_id: The user's unique ID.
        jti: Unique ID for this refresh token (JWT ID).
        refresh_token: The actual refresh token string.
        metadata: Optional details (IP, user_agent, etc.)
        ttl: Time-to-live in seconds.
    """
    if not redis_client:
        logger.error("Redis is not connected.")
        raise ConnectionError("Redis is not connected.")
    key = f"{SESSION_PREFIX}:{user_id}:{jti}"
    session_data = {
        "refresh_token": refresh_token,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(seconds=ttl)).isoformat(),
        "metadata": metadata or {},
    }
    await redis_client.setex(key, ttl, json.dumps(session_data))
    return True


async def get_session(user_id: str, jti: str) -> Optional[dict[str, Any]]:
    """Retrieve a user's session from Redis."""
    key = f"{SESSION_PREFIX}:{user_id}:{jti}"
    data = await redis_client.get(key)
    return json.loads(data) if data else None


async def rotate_session(
    user_id: str,
    old_jti: str,
    new_jti: str,
    new_refresh_token: str,
    metadata: dict | None = None,
    ttl: int = REFRESH_TOKEN_TTL,
) -> bool:
    """
    Rotate (replace) a refresh session with a new JTI and token.
    """
    old_key = f"{SESSION_PREFIX}:{user_id}:{old_jti}"
    await redis_client.delete(old_key)

    new_key = f"{SESSION_PREFIX}:{user_id}:{new_jti}"
    session_data = {
        "refresh_token": new_refresh_token,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(seconds=ttl)).isoformat(),
        "metadata": metadata or {},
    }
    await redis_client.setex(new_key, ttl, json.dumps(session_data))
    return True


async def revoke_session(user_id: str, jti: str) -> bool:
    """Revoke a single session (logout single device)."""
    key = f"{SESSION_PREFIX}:{user_id}:{jti}"
    deleted = await redis_client.delete(key)
    return bool(deleted)


async def revoke_all_sessions(user_id: str) -> int:
    """Revoke all sessions for a user (logout all devices)."""
    pattern = f"{SESSION_PREFIX}:{user_id}:*"
    keys = await redis_client.keys(pattern)
    if keys:
        return await redis_client.delete(*keys)
    return 0


async def blacklist_token(jti: str, ttl: int = BLACKLIST_TTL) -> bool:
    """Add a token's JTI to blacklist."""
    key = f"{BLACKLIST_PREFIX}:{jti}"
    await redis_client.setex(key, ttl, "true")
    return True


async def is_token_blacklisted(jti: str) -> bool:
    """Check if token's JTI is blacklisted."""
    key = f"{BLACKLIST_PREFIX}:{jti}"
    return bool(await redis_client.exists(key))


async def list_active_sessions(user_id: str) -> list[dict[str, Any]]:
    """List all active sessions for a user."""
    pattern = f"{SESSION_PREFIX}:{user_id}:*"
    keys = await redis_client.keys(pattern)
    sessions = []
    for key in keys:
        data = await redis_client.get(key)
        if data:
            sessions.append(json.loads(data))
    return sessions


async def user_login(data: dict, metadata: dict | None = None) -> dict:
    email = data.get("email", None)
    password = data.get("password", None)
    username = data.get("username", None)
    user_repo = BaseRepository(User)
    query = Or(User.email == email, User.username == username)
    user = await user_repo.find_one(query)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or username is incorrect.",
        )

    if not verify_password(password=password, hashed=user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Entered password is incorrect.",
        )

    if user.is_superuser:
        role = "admin"
    else:
        role = "user"

    session_id = str(uuid.uuid4())

    access_token = create_access_token(subject=str(user.id), token_version=1, role=role)
    refresh_token = create_refresh_token(subject=str(user.id), session_id=session_id)

    payload = verify_token(refresh_token, expected_type="refresh")
    refresh_jti = payload.get("jti")
    expiry_timestamp = payload.get("exp")
    ttl = int(expiry_timestamp - int(datetime.now(timezone.utc).timestamp()))

    await create_session(
        user_id=str(user.id),
        jti=refresh_jti,
        refresh_token=refresh_token,
        metadata=metadata or {},
        ttl=ttl,
    )

    logger.info(
        "User logged in",
        extra={"extra": {"user_id": str(user.id), "session_id": session_id}},
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "session_id": session_id,
        "access_expires_in": env.access_token_expire_seconds,
        "refresh_expires_in": ttl,
    }


async def logout_current_session(presented_refresh_token: str) -> bool:
    payload = verify_token(presented_refresh_token, expected_type="refresh")
    jti = payload.get("jti")
    user_id = payload.get("sub")
    if not jti or not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )

    await revoke_session(user_id, jti)

    now_ts = int(datetime.now(timezone.utc).timestamp())
    exp_ts = int(payload.get("exp", now_ts))
    remaining = max(1, exp_ts - now_ts)
    await blacklist_token(jti, ttl=remaining)

    logger.info("Session logged out", extra={"extra": {"user_id": user_id, "jti": jti}})
    return True
