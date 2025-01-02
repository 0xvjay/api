from datetime import datetime

from pydantic import UUID4, BaseModel, Field

from .constant import VoteEnum


class BaseProductReviewSchema(BaseModel):
    rating: int = Field(ge=0, le=5)
    title: str
    body: str
    product_id: UUID4


class ProductReviewCreateSchema(BaseProductReviewSchema):
    pass


class ProductReviewUpdateSchema(BaseProductReviewSchema):
    id: UUID4


class ProductReviewOutMinimalSchema(ProductReviewUpdateSchema):
    user_id: UUID4


class ProductReviewOutSchema(ProductReviewOutMinimalSchema):
    total_votes: int

    created_at: datetime
    updated_at: datetime | None


class BaseVoteSchema(BaseModel):
    vote: VoteEnum


class VoteCreateSchema(BaseVoteSchema):
    pass


class VoteUpdateSchema(BaseVoteSchema):
    id: UUID4


class VoteOutShema(VoteUpdateSchema):
    created_at: datetime
    updated_at: datetime | None
