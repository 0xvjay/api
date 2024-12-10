from typing import List

from fastapi import Request
from pydantic import UUID4
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api.core.crud import CRUDBase

from .models import Group, Permission
from .schemas import GroupCreateSchema, GroupUpdateSchema


class CRUDGroup(CRUDBase[Group, GroupCreateSchema, GroupUpdateSchema]):
    async def get(
        self, request: Request, db_session: AsyncSession, id: UUID4
    ) -> Group | None:
        await self._create_get_log(request=request, db_session=db_session, id=id)
        result = await db_session.execute(
            select(Group).options(joinedload(Group.permissions)).where(Group.id == id)
        )
        return result.unique().scalar_one_or_none()

    async def list(
        self,
        request: Request,
        db_session: AsyncSession,
        query_str: str | None = None,
        order_by: str | None = None,
    ) -> List[Group]:
        await self._create_list_log(request=request, db_session=db_session)
        query = select(Group)

        if query_str:
            query = query.where(
                (Group.name.contains(query_str) | Group.description.contains(query_str))
            )

        if order_by:
            order_criteria = []
            fields = [field.strip() for field in order_by.split(",")]
            for field in fields:
                if field.startswith("-"):
                    order_criteria.append(desc(getattr(Group, field[1:])))
                else:
                    order_criteria.append(getattr(Group, field))
            query = query.order_by(*order_criteria)

        result = await db_session.execute(query)
        return result.unique().scalars().all()

    async def get_by_name(self, db_session: AsyncSession, name: str) -> Group | None:
        result = await db_session.execute(select(Group).where(Group.name == name))
        return result.unique().scalar_one_or_none()

    async def create(
        self, request: Request, db_session: AsyncSession, group: GroupCreateSchema
    ) -> Group:
        await self._create_add_log(request=request, db_session=db_session)
        db_group = Group(**group.model_dump(exclude={"permissions"}))
        if group.permissions:
            db_group.permissions.clear()

            permission_ids = [permission.id for permission in group.permissions]

            permissions_result = await db_session.execute(
                select(Permission).where(Permission.id.in_(permission_ids))
            )
            permissions = permissions_result.scalars().all()
            db_group.permissions.extend(permissions)

        db_session.add(db_group)
        await db_session.commit()
        await db_session.refresh(db_group)
        return db_group

    async def update(
        self,
        request: Request,
        db_session: AsyncSession,
        db_group: Group,
        group: GroupUpdateSchema,
    ):
        await self._create_update_log(request=request, db_session=db_session)
        for key, value in group.model_dump(exclude={"permissions"}).items():
            setattr(db_group, key, value)

        if group.permissions:
            db_group.permissions.clear()

            permission_ids = [permission.id for permission in group.permissions]

            permissions_result = await db_session.execute(
                select(Permission).where(Permission.id.in_(permission_ids))
            )
            permissions = permissions_result.scalars().all()
            db_group.permissions.extend(permissions)

        await db_session.commit()
        await db_session.refresh(db_group)
        return db_group


async def get_permissions(db_session: AsyncSession) -> List[Permission]:
    result = await db_session.execute(select(Permission))
    return result.scalars().all()


group_crud = CRUDGroup(Group, "Group")
