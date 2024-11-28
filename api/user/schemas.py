from datetime import datetime
from typing import List

from pydantic import UUID4, BaseModel, EmailStr, Field

from api.auth.schemas import GroupOutMinimalSchema
from api.address.schemas import BaseAddressSchema


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


class UserOutMinimalSchema(BaseUserSchema):
    id: UUID4
    last_login: datetime | None
    groups: List["GroupOutMinimalSchema"] = []


class UserOutSchema(UserOutMinimalSchema):
    created_at: datetime
    updated_at: datetime | None = None


class UserAddressCreateSchema(BaseAddressSchema):
    phone_number: str
    notes: str | None = None
    is_default_for_shipping: bool
    is_default_for_billing: bool


class UserAddressUpdateSchema(UserAddressCreateSchema):
    id: UUID4


class UserAddressOutSchema(UserAddressUpdateSchema):
    pass
