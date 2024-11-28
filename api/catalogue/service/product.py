from typing import List

from pydantic import UUID4
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Product, SubCategory
from ..schemas import ProductCreateSchema, ProductUpdateSchema


async def retrieve(db_session: AsyncSession, id: UUID4) -> Product | None:
    result = await db_session.execute(select(Product).where(Product.id == id))
    return result.unique().scalar_one_or_none()


async def get_by_name(db_session: AsyncSession, name: str) -> Product | None:
    result = await db_session.execute(select(Product).where(Product.name == name))
    return result.unique().scalar_one_or_none()


async def get(
    db_session: AsyncSession, query_str: str | None = None, order_by: str | None = None
) -> List[Product]:
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


async def create(db_session: AsyncSession, product: ProductCreateSchema) -> Product:
    db_product = Product(**product.model_dump(exclude={"sub_categories"}))

    if product.sub_categories:
        db_product.sub_categories.clear()

        sub_category_ids = [sub_category.id for sub_category in product.sub_categories]

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
    db_session: AsyncSession,
    product: ProductUpdateSchema,
    db_product: Product,
) -> Product:
    for key, value in product.model_dump(exclude={"sub_categories"}).items():
        setattr(db_product, key, value)

    if product.sub_categories:
        db_product.sub_categories.clear()

        sub_category_ids = [sub_category.id for sub_category in product.sub_categories]

        sub_categories_result = await db_session.execute(
            select(SubCategory).where(SubCategory.id.in_(sub_category_ids))
        )
        sub_categories = sub_categories_result.unique().scalars().all()
        db_product.sub_categories.extend(sub_categories)

    await db_session.commit()
    await db_session.refresh(db_product)
    return db_product


async def delete(db_session: AsyncSession, db_product: Product) -> None:
    await db_session.delete(db_product)
    await db_session.commit()
    return
