from pydantic import UUID4
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..exceptions import GroupNotFound
from ..models import Group
from ..schemas import GroupCreateSchema, GroupUpdateSchema


async def retrieve(db_session: AsyncSession, id: UUID4) -> Group:
    result = await db_session.execute(select(Group).where(Group.id == id))
    return result.scalar_one_or_none()


async def get(
    db_session: AsyncSession,
    query_str: str | None = None,
    order_by: str | None = None,
):
    query = select(Group)

    if query_str:
        query = query.where(
            (Group.name.contains(query_str) | Group.description.contains(query_str))
        )

    if order_by:
        order_criteria = []
        for field in order_by:
            if field.startswith("-"):
                order_criteria.append(desc(getattr(Group, field[1:])))
            else:
                order_criteria.append(getattr(Group, field))
        query = query.order_by(*order_criteria)

    result = await db_session.execute(query)
    return result.scalars().all()


async def get_by_name(db_session: AsyncSession, name: str) -> Group | None:
    result = await db_session.execute(select(Group).where(Group.name == name))
    return result.scalar_one_or_none()


async def create(db_session: AsyncSession, group: GroupCreateSchema) -> Group:
    obj_data = Group(**group.model_dump())
    db_session.add(obj_data)
    await db_session.commit()
    await db_session.refresh(obj_data)
    return obj_data


async def update(db_session: AsyncSession, group: GroupUpdateSchema) -> Group:
    result = await db_session.execute(select(Group).where(Group.id == group.id))
    obj_data = result.scalar_one_or_none()

    if obj_data is None:
        raise GroupNotFound()

    for key, value in group.model_dump().items():
        setattr(obj_data, key, value)

    await db_session.commit()
    await db_session.refresh(obj_data)
    return obj_data


async def delete(db_session: AsyncSession, id: UUID4) -> None:
    result = await db_session.execute(select(Group).where(Group.id == id))
    db_group = result.scalar_one_or_none()

    if db_group:
        await db_session.delete(db_group)
        await db_session.commit()
    return
