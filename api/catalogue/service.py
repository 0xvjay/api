from typing import List

from fastapi import Request
from pydantic import UUID4
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api.core.crud import CRUDBase

from .models import Category, Product, SubCategory
from .schemas import (
    CategoryCreateSchema,
    CategoryUpdateSchema,
    ProductCreateSchema,
    ProductUpdateSchema,
    SubCategoryCreateSchema,
    SubCategoryUpdateSchema,
)


class CRUDCategory(CRUDBase[Category, CategoryCreateSchema, CategoryUpdateSchema]):
    async def get(
        self, request: Request, db_session: AsyncSession, id: UUID4
    ) -> Category | None:
        await self._create_get_log(request=request, db_session=db_session, id=id)
        result = await db_session.execute(
            select(Category)
            .options(joinedload(Category.sub_categories))
            .where(Category.id == id)
        )
        return result.unique().scalar_one_or_none()

    async def list(
        self,
        request: Request,
        db_session: AsyncSession,
        query_str: str | None = None,
        order_by: str | None = None,
    ) -> List[Category]:
        await self._create_list_log(request=request, db_session=db_session)
        query = select(Category).options(joinedload(Category.sub_categories))

        if query_str:
            query = query.where(Category.name.contains(query_str))

        if order_by:
            order_criteria = []
            fields = [field.strip() for field in order_by.split(",")]
            for field in fields:
                if field.startswith("-"):
                    order_criteria.append(desc(getattr(Category, field[1:])))
                else:
                    order_criteria.append(getattr(Category, field))
            query = query.order_by(*order_criteria)

        result = await db_session.execute(query)
        return result.unique().scalars().all()

    async def get_by_name(self, db_session: AsyncSession, name: str) -> Category | None:
        result = await db_session.execute(select(Category).where(Category.name == name))
        return result.unique().scalar_one_or_none()

    async def create(
        self, request: Request, db_session: AsyncSession, category: CategoryCreateSchema
    ) -> Category:
        await self._create_add_log(request=request, db_session=db_session)
        db_category = Category(**category.model_dump(exclude={"sub_categories"}))

        if category.sub_categories:
            db_category.sub_categories.clear()

            sub_category_ids = [
                sub_category.id for sub_category in category.sub_categories
            ]

            sub_categories_result = await db_session.execute(
                select(SubCategory).where(SubCategory.id.in_(sub_category_ids))
            )
            sub_categories = sub_categories_result.unique().scalars().all()
            db_category.sub_categories.extend(sub_categories)

        db_session.add(db_category)
        await db_session.commit()

        result = await db_session.execute(
            select(Category)
            .options(joinedload(Category.sub_categories))
            .where(Category.id == db_category.id)
        )
        return result.unique().scalar_one()

    async def update(
        self,
        request: Request,
        db_session: AsyncSession,
        db_category: Category,
        category: CategoryUpdateSchema,
    ) -> Category:
        await self._create_update_log(request=request, db_session=db_session)
        for key, value in category.model_dump(exclude={"sub_categories"}).items():
            setattr(db_category, key, value)

        if category.sub_categories:
            db_category.sub_categories.clear()

            sub_category_ids = [
                sub_category.id for sub_category in category.sub_categories
            ]

            sub_categories_result = await db_session.execute(
                select(SubCategory).where(SubCategory.id.in_(sub_category_ids))
            )
            sub_categories = sub_categories_result.unique().scalars().all()
            db_category.sub_categories.extend(sub_categories)

        await db_session.commit()
        await db_session.refresh(db_category)
        return db_category


class CRUDSubCategory(
    CRUDBase[SubCategory, SubCategoryCreateSchema, SubCategoryUpdateSchema]
):
    async def get(
        self, request: Request, db_session: AsyncSession, id: UUID4
    ) -> SubCategory | None:
        await self._create_get_log(request=request, db_session=db_session, id=id)
        result = await db_session.execute(
            select(SubCategory)
            .options(joinedload(SubCategory.products))
            .where(SubCategory.id == id)
        )
        return result.unique().scalar_one_or_none()

    async def get_by_name(
        self, db_session: AsyncSession, name: str
    ) -> SubCategory | None:
        result = await db_session.execute(
            select(SubCategory).where(SubCategory.name == name)
        )
        return result.unique().scalar_one_or_none()


class CRUDProduct(CRUDBase[Product, ProductCreateSchema, ProductUpdateSchema]):
    async def get(
        self, request: Request, db_session: AsyncSession, id: UUID4
    ) -> Product | None:
        await self._create_get_log(request=request, db_session=db_session, id=id)
        result = await db_session.execute(
            select(Product)
            .options(joinedload(Product.sub_categories))
            .where(Product.id == id)
        )
        return result.unique().scalar_one_or_none()

    async def get_by_name(self, db_session: AsyncSession, name: str) -> Product | None:
        result = await db_session.execute(select(Product).where(Product.name == name))
        return result.unique().scalar_one_or_none()

    async def list(
        self,
        request: Request,
        db_session: AsyncSession,
        query_str: str | None = None,
        order_by: str | None = None,
    ) -> List[Product]:
        await self._create_list_log(request=request, db_session=db_session)
        query = select(Product)

        if query_str:
            query = query.where(
                (
                    Product.name.contains(query_str)
                    | Product.description.contains(query_str)
                    | Product.short_description.contains(query_str)
                )
            )

        if order_by:
            order_criteria = []
            fields = [field.strip() for field in order_by.split(",")]
            for field in fields:
                if field.startswith("-"):
                    order_criteria.append(desc(getattr(Product, field[1:])))
                else:
                    order_criteria.append(getattr(Product, field))
            query = query.order_by(*order_criteria)

        result = await db_session.execute(query)
        return result.unique().scalars().all()

    async def create(
        self, request: Request, db_session: AsyncSession, product: ProductCreateSchema
    ) -> Product:
        await self._create_add_log(request=request, db_session=db_session)
        db_product = Product(**product.model_dump(exclude={"sub_categories"}))

        if product.sub_categories:
            db_product.sub_categories.clear()

            sub_category_ids = [
                sub_category.id for sub_category in product.sub_categories
            ]

            sub_categories_result = await db_session.execute(
                select(SubCategory).where(SubCategory.id.in_(sub_category_ids))
            )
            sub_categories = sub_categories_result.unique().scalars().all()
            db_product.sub_categories.extend(sub_categories)

        db_session.add(db_product)
        await db_session.commit()
        await db_session.refresh(db_product)
        return db_product

    async def update(
        self,
        request: Request,
        db_session: AsyncSession,
        db_product: Product,
        product: ProductUpdateSchema,
    ) -> Product:
        await self._create_update_log(request=request, db_session=db_session)
        for key, value in product.model_dump(exclude={"sub_categories"}).items():
            setattr(db_product, key, value)

        if product.sub_categories:
            db_product.sub_categories.clear()

            sub_category_ids = [
                sub_category.id for sub_category in product.sub_categories
            ]

            sub_categories_result = await db_session.execute(
                select(SubCategory).where(SubCategory.id.in_(sub_category_ids))
            )
            sub_categories = sub_categories_result.unique().scalars().all()
            db_product.sub_categories.extend(sub_categories)

        await db_session.commit()
        await db_session.refresh(db_product)
        return db_product


category_crud = CRUDCategory(Category, "Category")
sub_category_crud = CRUDSubCategory(SubCategory, "Sub Category")
product_crud = CRUDProduct(Product, "Product")
