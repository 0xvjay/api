from datetime import datetime

from pydantic import UUID4, BaseModel, EmailStr, Field


class BaseUserSchema(BaseModel):
    username: str
    email: EmailStr
    first_name: str | None = Field(None, min_length=3)
    last_name: str | None = Field(None, min_length=3)


class UserCreateSchema(BaseUserSchema):
    password: str = Field(min_length=6, max_length=128)


class UserUpdateSchema(BaseUserSchema):
    id: UUID4
    username: str | None = Field(None, min_length=3)
    email: EmailStr | None = Field(None)
    password: str | None = Field(None, min_length=6)
    is_active: bool


class UserOutMinimalSchema(UserUpdateSchema):
    last_login: datetime | None


class UserOutSchema(BaseUserSchema):
    created_at: datetime
    updated_at: datetime
