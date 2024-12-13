from datetime import date, datetime
from decimal import Decimal
from typing import List

from pydantic import UUID4, BaseModel, EmailStr, Field

from api.address.schemas import BaseAddressSchema
from api.auth.schemas import GroupOutMinimalSchema
from api.catalogue.schemas import ProductOutMinimalSchema


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


class UserOutSchema(UserOutMinimalSchema):
    created_at: datetime
    updated_at: datetime | None = None
    groups: List["GroupOutMinimalSchema"] = []


class UserAddressCreateSchema(BaseAddressSchema):
    phone_number: str
    notes: str | None = None
    is_default_for_shipping: bool
    is_default_for_billing: bool


class UserAddressUpdateSchema(UserAddressCreateSchema):
    id: UUID4


class UserAddressOutSchema(UserAddressUpdateSchema):
    pass


class BaseCompanySchema(BaseModel):
    billing_code: str
    email: str
    is_active: bool


class CompanyCreateSchema(BaseCompanySchema):
    password: str


class CompanyUpdateSchema(BaseCompanySchema):
    id: UUID4


class CompanyOutMinimalSchema(CompanyUpdateSchema):
    pass


class CompanyOutSchema(CompanyOutMinimalSchema):
    created_at: datetime
    updated_at: datetime | None


class BaseProjectSchema(BaseModel):
    name: str
    code: str
    description: str | None = None
    priority: int = 0
    start_date: date
    end_date: date


class ProjectCreateSchema(BaseProjectSchema):
    company_id: UUID4
    products: List["ProductLimitCreateSchema"] = []


class ProjectUpdateSchema(ProjectCreateSchema):
    id: UUID4


class ProjectOutMinimalSchema(BaseProjectSchema):
    id: UUID4
    company_id: UUID4


class ProjectOutSchema(ProjectOutMinimalSchema):
    company: CompanyOutMinimalSchema
    products: List["ProductLimitOutSchema"] = []
    created_at: datetime
    updated_at: datetime | None


class BaseProductLimit(BaseModel):
    product: ProductOutMinimalSchema
    amount: Decimal = Field(max_digits=12, decimal_places=2)
    absolute_limit: bool


class ProductLimitCreateSchema(BaseProductLimit):
    pass


class ProductLimitUpdateSchema(ProductLimitCreateSchema):
    id: UUID4
    project_id: UUID4


class ProductLimitOutMinimalSchema(ProductLimitUpdateSchema):
    pass


class ProductLimitOutSchema(ProductLimitOutMinimalSchema):
    product: ProductOutMinimalSchema


class BaseCreditSchema(BaseModel):
    user_id: UUID4
    project_id: UUID4
    amount: Decimal = Field(max_length=10, decimal_places=2)


class CreditCreateSchema(BaseCreditSchema):
    pass


class CreditUpdateSchema(CreditCreateSchema):
    id: UUID4


class CreditOutMinimalSchema(CreditUpdateSchema):
    pass


class CreditOutSchema(CreditOutMinimalSchema):
    created_at: datetime
    updated_at: datetime | None
