from decimal import Decimal
from typing import List

from pydantic import UUID4, BaseModel, EmailStr, Field

from api.catalogue.schemas import ProductOutMinimalSchema
from api.user.schemas import UserOutMinimalSchema

from .constant import OrderStatus


class BaseOrderSchema(BaseModel):
    guest_email: EmailStr | None = None


class OrderCreateSchema(BaseOrderSchema):
    lines: List["BaseLineSchema"]


class OrderUpdateSchema(BaseOrderSchema):
    id: UUID4
    status: OrderStatus


class OrderOutMinimalSchema(OrderUpdateSchema):
    total_incl_tax: Decimal = Field(max_digits=12, decimal_places=2)
    total_excl_tax: Decimal = Field(max_digits=12, decimal_places=2)


class OrderOutSchema(OrderOutMinimalSchema):
    shipping_incl_tax: Decimal = Field(0, max_digits=12, decimal_places=2)
    shipping_excl_tax: Decimal = Field(0, max_digits=12, decimal_places=2)

    user: UserOutMinimalSchema
    lines: List["LineOutSchema"]


class BaseLineSchema(BaseModel):
    quantity: int
    product: ProductOutMinimalSchema


class LineOutMinimalSchema(BaseLineSchema):
    id: UUID4


class LineOutSchema(LineOutMinimalSchema):
    line_price_incl_tax: Decimal = Field(max_digits=12, decimal_places=2)
    line_price_excl_tax: Decimal = Field(max_digits=12, decimal_places=2)
    line_price_before_discounts_incl_tax: Decimal = Field(
        max_digits=12, decimal_places=2
    )
    line_price_before_discounts_excl_tax: Decimal = Field(
        max_digits=12, decimal_places=2
    )
    unit_price_incl_tax: Decimal = Field(max_digits=12, decimal_places=2)
    unit_price_excl_tax: Decimal = Field(max_digits=12, decimal_places=2)
