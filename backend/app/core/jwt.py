import jwt
import uuid
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status

from app.core.config import env
from app.core.logging import get_logger

logger = get_logger("app.core.jwt")


def _load_private_key() -> Optional[str]:
    """Load private key contents from inline env or file path. Returns PEM or None."""
    try:
        if getattr(env, "jwt_private_key_pem", None):
            return env.jwt_private_key_pem
    except Exception:
        pass

    p = Path(getattr(env, "jwt_private_key_path", ""))
    if p and p.exists():
        try:
            return p.read_text()
        except Exception as e:
            logger.warning(f"Failed to read JWT private key file: {e}")
            return None

    logger.warning("JWT private key not found at path and no inline PEM provided")
    return None


def _load_public_key() -> Optional[str]:
    """Load public key contents from inline env or file path. Returns PEM or None."""
    try:
        if getattr(env, "jwt_public_key_pem", None):
            return env.jwt_public_key_pem
    except Exception:
        pass

    p = Path(getattr(env, "jwt_public_key_path", ""))
    if p and p.exists():
        try:
            return p.read_text()
        except Exception as e:
            logger.warning(f"Failed to read JWT public key file: {e}")
            return None

    logger.warning("JWT public key not found at path and no inline PEM provided")
    return None


_PRIVATE_KEY = _load_private_key()
_PUBLIC_KEY = _load_public_key()

_ALG = getattr(env, "jwt_algorithm", "EdDSA") or "EdDSA"
_KID = getattr(env, "jwt_kid", "default") or "default"

if not _PRIVATE_KEY:
    logger.warning(
        "No private key loaded — signing functions will fail until a private key is provided."
    )

if not _PUBLIC_KEY:
    logger.warning(
        "No public key loaded — token verification may fail until public key is available."
    )


def _now() -> datetime:
    return datetime.now(timezone.utc)


def new_jti() -> str:
    return str(uuid.uuid4())


def create_access_token(
    subject: str,
    *,
    expires_delta: Optional[timedelta] = None,
    scopes: Optional[list[str]] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
    token_version: Optional[int] = None,
    role: str,
) -> str:
    """
    Create an EdDSA-signed access token.
    - subject: typically the user id (string)
    - expires_delta: optional timedelta to override default expiry
    - scopes: optional list of scopes/permissions
    - extra_claims: optional dict to include additional claims
    - token_version: optional integer included as 'ver' claim for versioning invalidation
    """
    if not _PRIVATE_KEY:
        raise RuntimeError("JWT private key not loaded")

    now = _now()
    exp = now + (
        expires_delta
        if expires_delta
        else timedelta(seconds=getattr(env, "access_token_expire_seconds", 900))
    )
    jti = new_jti()

    payload: Dict[str, Any] = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "jti": jti,
        "typ": "access",
        "role": role,
    }

    if scopes:
        payload["scopes"] = scopes
    if token_version is not None:
        payload["ver"] = token_version
    if extra_claims:
        payload.update(extra_claims)

    headers = {"alg": _ALG, "kid": _KID, "typ": "JWT"}
    token = jwt.encode(payload, _PRIVATE_KEY, algorithm=_ALG, headers=headers)
    return token


def create_refresh_token(
    subject: str,
    session_id: str,
    *,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create an EdDSA-signed refresh token.
    - subject: user id (string)
    - session_id: unique session id (string, typically a UUID)
    - expires_delta: optional timedelta to override default expiry
    - extra_claims: optional dict to include additional claims
    """
    if not _PRIVATE_KEY:
        raise RuntimeError("JWT private key not loaded")

    now = _now()
    exp = now + (
        expires_delta
        if expires_delta
        else timedelta(seconds=getattr(env, "refresh_token_expire_seconds", 1209600))
    )
    jti = new_jti()

    payload: Dict[str, Any] = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "jti": jti,
        "typ": "refresh",
        "session_id": str(session_id),
    }

    if extra_claims:
        payload.update(extra_claims)

    headers = {"alg": _ALG, "kid": _KID, "typ": "JWT"}
    token = jwt.encode(payload, _PRIVATE_KEY, algorithm=_ALG, headers=headers)
    return token


def verify_token(token: str, expected_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Verify signature and required claims. Returns payload dict.
    Raises HTTPException on failure (401 for auth issues, 500 for config).
    """
    if not _PUBLIC_KEY:
        logger.error("Public key not configured for JWT verification")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Public key not configured",
        )

    try:
        options = {"require": ["exp", "iat", "nbf", "jti", "sub"]}
        payload = jwt.decode(token, _PUBLIC_KEY, algorithms=[_ALG], options=options)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except jwt.InvalidSignatureError:
        logger.warning("JWT signature verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token signature"
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    if expected_type and payload.get("typ") != expected_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
        )

    return payload
