from typing import List

from pydantic import UUID4, EmailStr
from sqlalchemy import desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.models import Group

from .models import User
from .schemas import UserCreateSchema, UserUpdateSchema


async def get(
    db_session: AsyncSession,
    query_str: str | None = None,
    order_by: str | None = None,
) -> List[User]:
    query = select(User)

    if query_str:
        query = query.where(
            (
                User.username.contains(query_str)
                | User.email.contains(query_str)
                | User.first_name.contains(query_str)
                | User.last_name.contains(query_str)
            )
        )

    if order_by:
        order_criteria = []
        fields = [field.strip() for field in order_by.split(",")]
        for field in fields:
            if field.startswith("-"):
                order_criteria.append(desc(getattr(User, field[1:])))
            else:
                order_criteria.append(getattr(User, field))
        query = query.order_by(*order_criteria)

    result = await db_session.execute(query)
    return result.unique().scalars().all()


async def retrieve(db_session: AsyncSession, id: UUID4) -> User | None:
    result = await db_session.execute(select(User).where(User.id == id))
    return result.unique().scalar_one_or_none()


async def get_by_email_or_username(
    db_session: AsyncSession, email: EmailStr | None = None, username: str | None = None
) -> User | None:
    if not email and not username:
        raise ValueError("Either email or username must be provided")
    query = select(User)
    conditions = []

    if email:
        conditions.append(User.email == email)
    if username:
        conditions.append(User.username == username)

    query = query.where(or_(*conditions))

    result = await db_session.execute(query)
    return result.unique().scalar_one_or_none()


async def create(db_session: AsyncSession, user: UserCreateSchema) -> User:
    db_user = User(**user.model_dump(exclude={"groups"}))
    if user.groups:
        db_user.groups.clear()

        group_ids = [group.id for group in user.groups]

        groups_result = await db_session.execute(
            select(Group).where(Group.id.in_(group_ids))
        )
        groups = groups_result.unique().scalars().all()
        db_user.groups.extend(groups)

    db_session.add(db_user)
    await db_session.commit()
    await db_session.refresh(db_user)
    return db_user


async def update(
    db_session: AsyncSession, user: UserUpdateSchema, user_id: UUID4
) -> User | None:
    result = await db_session.execute(select(User).where(User.id == user_id))
    db_user = result.unique().scalar_one_or_none()

    if db_user is None:
        return

    for key, value in user.model_dump(exclude={"groups"}).items():
        setattr(db_user, key, value)

    if user.groups:
        db_user.groups.clear()

        group_ids = [group.id for group in user.groups]

        groups_result = await db_session.execute(
            select(Group).where(Group.id.in_(group_ids))
        )
        groups = groups_result.unique().scalars().all()
        db_user.groups.extend(groups)

    await db_session.commit()
    await db_session.refresh(db_user)
    return db_user


async def delete(db_session: AsyncSession, id: UUID4) -> bool:
    result = await db_session.execute(select(User).where(User.id == id))
    db_user = result.unique().scalar_one_or_none()

    if db_user:
        await db_session.delete(db_user)
        await db_session.commit()
        return True
    return False
