from typing import List

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import SubCategory
from ..schemas import SubCategoryCreateSchema, SubCategoryUpdateSchema


async def retrieve(db_session: AsyncSession, id: UUID4) -> SubCategory | None:
    result = await db_session.execute(select(SubCategory).where(SubCategory.id == id))
    return result.unique().scalar_one_or_none()


async def get_by_name(db_session: AsyncSession, name: str) -> SubCategory | None:
    result = await db_session.execute(
        select(SubCategory).where(SubCategory.name == name)
    )
    return result.unique().scalar_one_or_none()


async def get(db_session: AsyncSession) -> List[SubCategory]:
    result = await db_session.execute(select(SubCategory))
    return result.unique().scalars().all()


async def create(
    db_session: AsyncSession, sub_category: SubCategoryCreateSchema
) -> SubCategory:
    db_subcategory = SubCategory(**sub_category.model_dump())
    db_session.add(db_subcategory)
    await db_session.commit()
    await db_session.refresh(db_subcategory)
    return db_subcategory


async def update(
    db_session: AsyncSession,
    sub_category: SubCategoryUpdateSchema,
    db_subcategory: SubCategory,
) -> SubCategory:
    for key, value in sub_category.model_dump().items():
        setattr(db_subcategory, key, value)

    await db_session.commit()
    await db_session.refresh(db_subcategory)
    return db_subcategory


async def delete(db_session: AsyncSession, db_subcategory: SubCategory) -> None:
    await db_session.delete(db_subcategory)
    await db_session.commit()
    return
