from typing import List

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Category, SubCategory
from ..schemas import (
    CategoryCreateSchema,
    CategoryUpdateSchema,
)


async def retrieve(db_session: AsyncSession, id: UUID4) -> Category | None:
    result = await db_session.execute(select(Category).where(Category.id == id))
    return result.unique().scalar_one_or_none()


async def get(db_session: AsyncSession) -> List[Category]:
    result = await db_session.execute(select(Category))
    return result.unique().scalars().all()


async def get_by_name(db_session: AsyncSession, name: str) -> Category | None:
    result = await db_session.execute(select(Category).where(Category.name == name))
    return result.unique().scalar_one_or_none()


async def create(db_session: AsyncSession, category: CategoryCreateSchema) -> Category:
    db_category = Category(**category.model_dump(exclude={"sub_categories"}))

    if category.sub_categories:
        db_category.sub_categories.clear()

        sub_category_ids = [sub_category.id for sub_category in category.sub_categories]

        sub_categories_result = await db_session.execute(
            select(SubCategory).where(SubCategory.id.in_(sub_category_ids))
        )
        sub_categories = sub_categories_result.unique().scalars().all()
        db_category.sub_categories.extend(sub_categories)

    db_session.add(db_category)
    await db_session.commit()
    await db_session.refresh(db_category)
    return db_category


async def update(
    db_session: AsyncSession, category: CategoryUpdateSchema, db_category: Category
) -> Category:
    for key, value in category.model_dump(exclude={"sub_categories"}).items():
        setattr(db_category, key, value)

    if category.sub_categories:
        db_category.sub_categories.clear()

        sub_category_ids = [sub_category.id for sub_category in category.sub_categories]

        sub_categories_result = await db_session.execute(
            select(SubCategory).where(SubCategory.id.in_(sub_category_ids))
        )
        sub_categories = sub_categories_result.unique().scalars().all()
        db_category.sub_categories.extend(sub_categories)

    await db_session.commit()
    await db_session.refresh(db_category)
    return db_category


async def delete(db_session: AsyncSession, db_category: Category) -> None:
    await db_session.delete(db_category)
    await db_session.commit()
    return
