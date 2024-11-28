from datetime import datetime
from typing import List

from pydantic import UUID4, BaseModel, Field
from decimal import Decimal


class BaseCategorySchema(BaseModel):
    name: str = Field(min_length=3)
    is_active: bool


class CategoryCreateSchema(BaseCategorySchema):
    sub_categories: List["SubCategoryOutMinimalSchema"] = []


class CategoryUpdateSchema(CategoryCreateSchema):
    id: UUID4


class CategoryOutSchema(CategoryUpdateSchema):
    pass


class BaseSubCategorySchema(BaseModel):
    name: str = Field(min_length=3)
    is_active: bool


class SubCategoryCreateSchema(BaseSubCategorySchema):
    pass


class SubCategoryUpdateSchema(SubCategoryCreateSchema):
    id: UUID4


class SubCategoryOutMinimalSchema(SubCategoryUpdateSchema):
    slug: str


class SubCategoryOutSchema(SubCategoryOutMinimalSchema):
    products: List["ProductOutMinimalSchema"]


class BaseProductSchema(BaseModel):
    name: str = Field(min_length=3)
    price: Decimal = Field(max_digits=10, decimal_places=2)
    is_active: bool
    is_discountable: bool
    description: str | None = None
    short_description: str | None = None


class ProductCreateSchema(BaseProductSchema):
    sub_categories: List["SubCategoryOutMinimalSchema"] = []


class ProductUpdateSchema(ProductCreateSchema):
    id: UUID4


class ProductOutMinimalSchema(BaseProductSchema):
    id: UUID4
    slug: str
    rating: float = Field(ge=0)


class ProductOutSchema(ProductOutMinimalSchema):
    created_at: datetime
    updated_at: datetime | None = None
