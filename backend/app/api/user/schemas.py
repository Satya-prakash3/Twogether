import re
from datetime import datetime
from pydantic_core import PydanticCustomError
from pydantic import EmailStr, BaseModel, Field, field_validator, field_serializer
from typing import Optional, Annotated

from app.common.utils import ISTTimeStampedResponse


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr | None = None
    password: str = Field(..., min_length=8)
    admin: Optional[bool] = False

    @field_validator("username")
    @classmethod
    def username_validator(cls, value):
        if len(value) > 50:
            raise PydanticCustomError("value_error", "Username too long.")
        elif len(value) < 3:
            raise PydanticCustomError("value_error", "Username too short.")
        else:
            return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):
        if len(value) < 8:
            raise PydanticCustomError(
                "password_too_short", "Password must be at least 8 characters long."
            )

        if not re.search(r"[A-Z]", value):
            raise PydanticCustomError(
                "password_no_uppercase",
                "Password must contain at least one uppercase letter.",
            )

        if not re.search(r"[a-z]", value):
            raise PydanticCustomError(
                "password_no_lowercase",
                "Password must contain at least one lowercase letter.",
            )

        if not re.search(r"[0-9]", value):
            raise PydanticCustomError(
                "password_no_digit", "Password must contain at least one number."
            )

        if not re.search(r"[@$!%*?&#^+=_.,;:-]", value):
            raise PydanticCustomError(
                "password_no_special",
                "Password must contain at least one special character.",
            )

        return value


class UserResponse(ISTTimeStampedResponse):
    id: str
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime


class UserView(ISTTimeStampedResponse):
    id: str = Field(alias="_id")
    username: str
    email: EmailStr
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
