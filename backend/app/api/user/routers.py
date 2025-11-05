from fastapi import (
    APIRouter,
    status
)

from app.api.user.schemas import (
    UserRegister,
    UserResponse,
    UserView
)
from app.api.user.services import (
    register_user,
    get_users
)
from app.common.utils import (
    SuccessResponse,
    SuccessResponseForData
)


user_router = APIRouter()

@user_router.post("/register",response_model=SuccessResponse[UserResponse],status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister):
    user = await register_user(data=payload)
    user = UserResponse(
        id = str(user.id),
        username = user.username,
        email = user.email,
        created_at = user.created_at,
        updated_at = user.updated_at
    )
    return SuccessResponse(message="Registration Successful.", data=user)

@user_router.get("/allUsers", response_model=SuccessResponseForData[list], status_code=status.HTTP_200_OK)
async def get_all_users():
    user = await get_users()
    return SuccessResponseForData(data=user)