from typing import Generic, List, Type, TypeVar

from pydantic import UUID4, BaseModel
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db_session: AsyncSession, id: UUID4) -> ModelType | None:
        result = await db_session.execute(select(self.model).where(self.model.id == id))
        return result.unique().scalar_one_or_none()

    async def list(
        self,
        db_session: AsyncSession,
        query_str: str | None = None,
        order_by: str | None = None,
    ) -> List[ModelType]:
        query = select(self.model)

        if query_str:
            pass
            # override based on model fields

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

    async def create(
        self, db_session: AsyncSession, schema: CreateSchemaType
    ) -> ModelType:
        db_obj = self.model(**schema.model_dump())
        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj

    async def update(
        self, db_session: AsyncSession, db_obj: ModelType, schema: UpdateSchemaType
    ) -> ModelType:
        obj_data = schema.model_dump(exclude_unset=True)
        for key, value in obj_data.items():
            setattr(db_obj, key, value)

        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj

    async def delete(self, db_session: AsyncSession, db_obj: ModelType) -> None:
        await db_session.delete(db_obj)
        await db_session.commit()
