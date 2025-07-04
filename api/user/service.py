from typing import List

from fastapi import Request
from pydantic import UUID4, EmailStr
from sqlalchemy import desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api.address.models import UserAddress
from api.auth.models import Group
from api.auth.security import get_password_hash
from api.catalogue.models import Product
from api.core.crud import CRUDBase

from .models import Company, ProductLimit, Project, User
from .schemas import (
    CompanyCreateSchema,
    CompanyUpdateSchema,
    ProjectCreateSchema,
    ProjectUpdateSchema,
    UserAddressCreateSchema,
    UserAddressUpdateSchema,
    UserCreateSchema,
    UserUpdateSchema,
)


class CRUDUser(CRUDBase[User, UserCreateSchema, UserUpdateSchema]):
    async def get(
        self, request: Request, db_session: AsyncSession, id: UUID4
    ) -> User | None:
        await self._create_get_log(request=request, db_session=db_session, id=id)
        result = await db_session.execute(
            select(User).options(joinedload(User.groups)).where(User.id == id)
        )
        return result.unique().scalar_one_or_none()

    async def list(
        self,
        request: Request,
        db_session: AsyncSession,
        query_str: str | None = None,
        order_by: str | None = None,
    ) -> List[User]:
        await self._create_list_log(request=request, db_session=db_session)
        query = select(User)

        if query_str:
            query = query.where(
                or_(
                    User.username.contains(query_str),
                    User.email.contains(query_str),
                    User.first_name.contains(query_str),
                    User.last_name.contains(query_str),
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

    async def get_by_email_or_username(
        self,
        db_session: AsyncSession,
        email: EmailStr | None = None,
        username: str | None = None,
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

    async def create(
        self, request: Request, db_session: AsyncSession, user: UserCreateSchema
    ) -> User:
        await self._create_add_log(request=request, db_session=db_session)
        db_user = User(**user.model_dump(exclude={"groups"}))
        db_user.password = get_password_hash(user.password)
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
        self,
        request: Request,
        db_session: AsyncSession,
        db_user: User,
        user: UserUpdateSchema,
    ) -> User:
        await self._create_update_log(request=request, db_session=db_session)
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


class CRUDUserAddress(
    CRUDBase[UserAddress, UserAddressCreateSchema, UserAddressUpdateSchema]
):
    async def list(
        self,
        request: Request,
        db_session: AsyncSession,
        user_id: UUID4,
        query_str: str | None = None,
        order_by: str | None = None,
    ) -> List[UserAddress]:
        await self._create_list_log(request=request, db_session=db_session)
        query = select(UserAddress).where(UserAddress.user_id == user_id)

        if query_str:
            pass

        if order_by:
            order_criteria = []
            fields = [field.strip() for field in order_by.split(",")]
            for field in fields:
                if field.startswith("-"):
                    order_criteria.append(desc(getattr(self.model, field[1:])))
                else:
                    order_criteria.append(getattr(self.model, field))
            query = query.order_by(*order_criteria)

        result = await db_session.execute(query)
        return result.unique().scalars().all()

    async def get(
        self, request: Request, db_session: AsyncSession, id: UUID4, user_id: UUID4
    ) -> UserAddress | None:
        await self._create_get_log(request=request, db_session=db_session, id=id)
        result = await db_session.execute(
            select(UserAddress).where(
                UserAddress.user_id == user_id, UserAddress.id == id
            )
        )
        return result.unique().scalar_one_or_none()

    async def create(
        self,
        request: Request,
        db_session: AsyncSession,
        schema: UserAddressCreateSchema,
        user_id: UUID4,
    ) -> UserAddress:
        await self._create_add_log(request=request, db_session=db_session)
        db_obj = UserAddress(**schema.model_dump(), user_id=user_id)
        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)

        return db_obj


class CRUDCompany(CRUDBase[Company, CompanyCreateSchema, CompanyUpdateSchema]):
    async def get_by_email(
        self,
        db_session: AsyncSession,
        email: EmailStr,
    ) -> Company | None:
        result = await db_session.execute(select(Company).where(Company.email == email))
        return result.unique().scalar_one_or_none()

    async def create(
        self, request: Request, db_session: AsyncSession, schema: CompanyCreateSchema
    ) -> Company:
        await self._create_add_log(request=request, db_session=db_session)

        db_obj = Company(**schema.model_dump())
        db_obj.password = get_password_hash(schema.password)

        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj


class CRUDProject(CRUDBase[Project, ProjectCreateSchema, ProjectUpdateSchema]):
    async def get(
        self, request: Request, db_session: AsyncSession, id: UUID4
    ) -> Project | None:
        await self._create_get_log(request=request, db_session=db_session, id=id)
        result = await db_session.execute(
            select(Project)
            .options(
                joinedload(Project.company),
                joinedload(Project.products),
                joinedload(Project.product_limits).joinedload(ProductLimit.product),
            )
            .where(Project.id == id)
        )
        return result.unique().scalar_one_or_none()

    async def create(
        self, request: Request, db_session: AsyncSession, schema: ProjectCreateSchema
    ) -> Project:
        await self._create_add_log(request=request, db_session=db_session)
        db_project = Project(**schema.model_dump(exclude={"products"}))

        if schema.products:
            product_ids = [
                product_limit.product.id for product_limit in schema.products
            ]
            products_result = await db_session.execute(
                select(Product).where(Product.id.in_(product_ids))
            )
            products = products_result.unique().scalars().all()
            db_project.products.extend(products)

            db_session.add(db_project)
            await db_session.flush()

            product_limits = [
                ProductLimit(
                    project_id=db_project.id,
                    product_id=product.product.id,
                    amount=product.amount,
                    absolute_limit=product.absolute_limit,
                )
                for product in schema.products
            ]
            db_session.add_all(product_limits)

        await db_session.commit()
        await db_session.refresh(db_project)
        return db_project

    async def update(
        self,
        request: Request,
        db_session: AsyncSession,
        db_obj: Project,
        schema: ProjectUpdateSchema,
    ) -> Project:
        await self._create_update_log(request=request, db_session=db_session)

        for key, value in schema.model_dump(exclude={"products"}).items():
            setattr(db_obj, key, value)

        if schema.products is not None:
            delete_query = select(ProductLimit).where(
                ProductLimit.project_id == db_obj.id
            )
            existing_limits = await db_session.execute(delete_query)
            for limit in existing_limits.scalars().all():
                await db_session.delete(limit)

            product_ids = [product.product.id for product in schema.products]
            products_result = await db_session.execute(
                select(Product).where(Product.id.in_(product_ids))
            )
            products = products_result.unique().scalars().all()
            db_obj.products = products

            new_limits = [
                ProductLimit(
                    project_id=db_obj.id,
                    product_id=product.product.id,
                    amount=product.amount,
                    absolute_limit=product.absolute_limit,
                )
                for product in schema.products
            ]
            db_session.add_all(new_limits)

        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj


user_crud = CRUDUser(User, "User")
user_address_crud = CRUDUserAddress(UserAddress, "User Address")
company_crud = CRUDCompany(Company, "Company")
project_crud = CRUDProject(Project, "Project")
