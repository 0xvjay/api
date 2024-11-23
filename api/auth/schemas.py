from datetime import datetime
from typing import List

from pydantic import UUID4, BaseModel, EmailStr, Field


class AuthSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class JWTSchema(BaseModel):
    id: UUID4 = Field(alias="sub")


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class BaseGroupSchema(BaseModel):
    name: str
    description: str
    is_active: bool


class GroupCreateSchema(BaseGroupSchema):
    pass


class GroupUpdateSchema(BaseGroupSchema):
    id: UUID4


class GroupOutMinimalSchema(GroupUpdateSchema):
    pass


class GroupOutSchema(GroupOutMinimalSchema):
    created_at: datetime
    updated_at: datetime

    permissions: List["PermissionOutMinimalSchema"]


class BasePermissionSchema(BaseModel):
    name: str
    description: str
    action: str
    object: str


class PermissionOutMinimalSchema(BasePermissionSchema):
    id: UUID4


class PermissionOutSchema(BasePermissionSchema):
    created_at: datetime
    updated_at: datetime
