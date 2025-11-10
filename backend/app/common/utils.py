import pytz
from fastapi import status
from datetime import datetime, timezone
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, field_serializer

from app.common.constants import Constants


T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Operation Successful"
    data: Optional[T] = None


def success_response(
    message: Optional[str] = None,
    data: dict | list | None = None,
    status_code: int = status.HTTP_200_OK,
) -> dict[str, any]:
    """
    Standard format for successful responses.
    Example:
        return success_response("User registered", {"id": user.id})
    """
    response = {
        "success": True,
        "message": message,
    }
    if data is not None:
        response["data"] = data
    # response["status_code"] = code
    return response


# class SuccessResponseForData(BaseModel, Generic[T]):
#     success: bool = True
#     data: Optional[T] = None


# def success_response(
#     data: dict | list | None = None, code: int = status.HTTP_200_OK
# ) -> dict[str, any]:
#     """
#     Standard format for successful responses.
#     Example:
#         return success_response("User registered", {"id": user.id})
#     """
#     response = {"success": True, "data": data}
#     return response


IST = pytz.timezone(Constants.TIME_ZONE)


def utc_now() -> datetime:
    """Always use UTC time."""
    return datetime.now(timezone.utc)


def to_ist(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=pytz.UTC)
    return dt.astimezone(IST)


# class ISTTimeStampedResponse(BaseModel):
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None

#     @field_serializer("created_at", "updated_at", when_used="always")
#     def convert_to_ist(self, value: Optional[datetime], _info):
#         if value is None:
#             return None
#         return to_ist(value).strftime("%Y-%m-%d %H:%M:%S")


def to_ist(dt: datetime) -> datetime:
    """Convert UTC datetime to IST."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=pytz.UTC)
    return dt.astimezone(pytz.timezone("Asia/Kolkata"))


class ISTTimeStampedResponse(BaseModel):
    """Base model that converts ALL datetime fields to IST when serializing."""

    @field_serializer("*", when_used="always")
    def serialize_any_datetime(self, value: any, _info):
        if isinstance(value, datetime):
            return to_ist(value).strftime("%Y-%m-%d %H:%M:%S")
        return value
