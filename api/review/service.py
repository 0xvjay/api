from fastapi import Request
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.crud import CRUDBase

from .models import ProductReview, Vote
from .schemas import (
    ProductReviewCreateSchema,
    ProductReviewUpdateSchema,
    VoteCreateSchema,
    VoteUpdateSchema,
)


class CRUDReview(
    CRUDBase[ProductReview, ProductReviewCreateSchema, ProductReviewUpdateSchema]
):
    async def create(
        self,
        request: Request,
        db_session: AsyncSession,
        schema: ProductReviewCreateSchema,
    ) -> ProductReview:
        await self._create_add_log(request=request, db_session=db_session)
        db_obj = self.model(**schema.model_dump())
        db_obj.user_id = request.state.user.id
        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj


class CRUDVote(CRUDBase[Vote, VoteCreateSchema, VoteUpdateSchema]):
    async def create(self, request, db_session, schema, review_id: UUID4):
        response = await super().create(request, db_session, schema)
        return response

    async def update(self, request, db_session, db_obj, schema, review_id: UUID4):
        response = await super().update(request, db_session, db_obj, schema)
        return response

    async def delete(self, request, db_session, db_obj, review_id: UUID4):
        response = await super().delete(request, db_session, db_obj)
        return response


review_crud = CRUDReview(ProductReview, "Review")
vote_crud = CRUDVote(Vote, "View")
