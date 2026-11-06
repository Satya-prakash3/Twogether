from fastapi import status
from sqlalchemy import or_
from fastapi.exceptions import HTTPException

from app.api.user.models import User
from app.core.logging import get_logger
from app.common.security import make_password
from app.db.postgres import get_postgres_session
from app.common.services import BaseRepositorySQL
from app.api.user.schemas import UserRegister, UserView

logger = get_logger("app.api.user.services")


async def register_user(data: UserRegister) -> any:
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")
    admin = data.get("admin", None)
    session = await get_postgres_session()
    or_query = (or_(User.email == email, User.username == username))
    user_repo = BaseRepositorySQL(User)
    existing_user = await user_repo.find_one(session=session, query=or_query)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists.",
        )

    hashed_password = make_password(password)
    final_payload = {
        "username": username,
        "email": email,
        "password": hashed_password,
        "is_active": True,
    }
    if admin:
        final_payload["is_superuser"] = True
    user = await user_repo.save(session=session, instance=User(**final_payload))
    logger.info("Registration Successful")
    return user


async def get_users() -> dict[any]:
    session = await get_postgres_session()
    user_repo = BaseRepositorySQL(User)
    users = await user_repo.find_all(session=session, query=None)
    print(users)
    logger.info("User Fetched Successfully")
    return users
