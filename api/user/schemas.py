from datetime import datetime
from typing import List

from pydantic import UUID4, BaseModel, EmailStr, Field

from api.auth.schemas import GroupOutMinimalSchema


class BaseUserSchema(BaseModel):
    username: str
    email: EmailStr
    first_name: str | None = Field(None, min_length=3)
    last_name: str | None = Field(None, min_length=3)
    is_active: bool


class UserCreateSchema(BaseUserSchema):
    password: str = Field(min_length=6, max_length=128)

    groups: List["GroupOutMinimalSchema"] = []


class UserUpdateSchema(UserCreateSchema):
    id: UUID4
    username: str | None = Field(None, min_length=3)
    email: EmailStr | None = Field(None)
    password: str | None = Field(None, min_length=6)


class UserOutMinimalSchema(UserUpdateSchema):
    last_login: datetime | None


class UserOutSchema(BaseUserSchema):
    created_at: datetime
    updated_at: datetime | None = None
