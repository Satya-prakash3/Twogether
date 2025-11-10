from fastapi import status
from fastapi.exceptions import HTTPException
from beanie.odm.operators.find.logical import Or

from app.core.logging import get_logger
from app.common.security import make_password, verify_password
from app.api.user.models import User
from app.api.user.schemas import UserRegister, UserResponse, UserView
from app.common.services import BaseRepository

logger = get_logger("app.api.user.services")


async def register_user(data: UserRegister) -> any:
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")
    admin = data.get("admin", None)
    or_query = Or(User.email == email, User.username == username)
    user_repo = BaseRepository(User)
    existing_user = await user_repo.find_one(or_query)
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
    user = await user_repo.save(User(**final_payload))
    logger.info("Registration Successful")
    return user


async def get_users() -> dict[any]:
    user_repo = BaseRepository(User)
    users = await user_repo.find_all(fields=UserView)
    logger.info("User Fetched Successfully")
    return users
