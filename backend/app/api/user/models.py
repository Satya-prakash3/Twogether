import uuid
from pydantic import EmailStr

from app.common.models import (
    BaseDocument,
    CreationMixin,
    UpdationMixin,
    BaseTimeStampMixin
)


class User(BaseDocument, BaseTimeStampMixin):
    username: str
    email: EmailStr
    password: str
    is_active: bool = True
    is_superuser: bool = False

    class Settings:
        name = "USERS"
        indexes = [
            "email",
            "username"
    ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "satya",
                "email": "satya@example.com",
                "password_hash": "hashedpassword123",
                "is_active": True
            }
        }
    
    def __str__(self):
        return f"Users Model."

    