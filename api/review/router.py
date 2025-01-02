import logging
from typing import List

from fastapi import APIRouter, Depends, Request, status
from pydantic import UUID4

from api.auth.permissions import ReviewPermissions, VotePermissions
from api.database import DBSession
from api.exceptions import DetailedHTTPException

from .exceptions import ReviewNotFound
from .schemas import (
    ProductReviewCreateSchema,
    ProductReviewOutMinimalSchema,
    ProductReviewOutSchema,
    ProductReviewUpdateSchema,
    VoteCreateSchema,
    VoteOutShema,
    VoteUpdateSchema,
)
from .service import review_crud, vote_crud

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get(
    "/",
    response_model=List[ProductReviewOutMinimalSchema],
    dependencies=[Depends(ReviewPermissions.read)],
)
async def read_reviews(request: Request, db_session: DBSession):
    try:
        result = await review_crud.list(request=request, db_session=db_session)
        return result
    except Exception as e:
        logger.exception(f"Failed to fetch reviews: {str(e)}")
        raise DetailedHTTPException()


@router.get(
    "/{review_id}",
    response_model=ProductReviewOutSchema,
    dependencies=[Depends(ReviewPermissions.read)],
)
async def read_review(request: Request, db_session: DBSession, review_id: UUID4):
    try:
        result = await review_crud.get(
            request=request, db_session=db_session, id=review_id
        )
        if result is None:
            raise ReviewNotFound()
        return result
    except ReviewNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to fetch review {review_id}: {str(e)}")
        raise DetailedHTTPException()


@router.post(
    "/",
    response_model=ProductReviewOutMinimalSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(ReviewPermissions.create)],
)
async def add_review(
    request: Request, db_session: DBSession, review: ProductReviewCreateSchema
):
    try:
        result = await review_crud.create(
            request=request, db_session=db_session, schema=review
        )
        return result
    except Exception as e:
        logger.exception(f"Failed to create review: {str(e)}")
        raise DetailedHTTPException()


@router.put(
    "/{review_id}",
    response_model=ProductReviewOutMinimalSchema,
    dependencies=[Depends(ReviewPermissions.update)],
)
async def edit_review(
    request: Request,
    db_session: DBSession,
    review: ProductReviewUpdateSchema,
    review_id: UUID4,
):
    try:
        db_review = await review_crud.get(
            request=request, db_session=db_session, id=review_id
        )
        if db_review is None:
            raise ReviewNotFound()

        result = await review_crud.update(
            request=request, db_session=db_session, db_obj=db_review, schema=review
        )
        return result
    except ReviewNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to update review {review_id}: {str(e)}")
        raise DetailedHTTPException()


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(ReviewPermissions.delete)],
)
async def remove_review(request: Request, db_session: DBSession, review_id: UUID4):
    try:
        db_review = await review_crud.get(
            request=request, db_session=db_session, id=review_id
        )
        if db_review is None:
            raise ReviewNotFound()
        await review_crud.delete(
            request=request, db_session=db_session, db_obj=db_review
        )
        return
    except ReviewNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete review {review_id}: {str(e)}")
        raise DetailedHTTPException()


@router.post(
    "/{review_id}/votes/",
    status_code=status.HTTP_201_CREATED,
    response_model=VoteOutShema,
    dependencies=[Depends(VotePermissions.create)],
)
async def add_vote(
    request: Request, db_session: DBSession, review_id: UUID4, vote: VoteCreateSchema
):
    try:
        db_review = review_crud.get(
            request=request, db_session=db_session, id=review_id
        )
        if db_review is None:
            raise ReviewNotFound()

        result = await vote_crud.create(
            request=request, db_session=db_session, schema=vote, review_id=review_id
        )
        return result
    except ReviewNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to create vote {review_id}: {str(e)}")
        raise DetailedHTTPException()


@router.put(
    "/{review_id}/votes/{vote_id}",
    response_model=VoteOutShema,
    dependencies=[Depends(VotePermissions.update)],
)
async def update_vote(
    request: Request,
    db_session: DBSession,
    vote: VoteUpdateSchema,
    review_id: UUID4,
    vote_id: UUID4,
):
    try:
        db_review = review_crud.get(
            request=request, db_session=db_session, id=review_id
        )
        if db_review is None:
            raise ReviewNotFound()
        db_vote = await vote_crud.get(
            request=request, db_session=db_session, id=vote_id
        )
        if db_vote is None:
            result = await vote_crud.create(
                request=request, db_session=db_session, schema=vote, review_id=review_id
            )
            return result

        result = await vote_crud.update(
            request=request,
            db_session=db_session,
            db_obj=db_vote,
            review_id=review_id,
            schema=vote,
        )
        return result
    except ReviewNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to update vote {review_id} {vote_id}: {str(e)}")
        raise DetailedHTTPException()


@router.delete(
    "/{review_id}/votes/{vote_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(VotePermissions.delete)],
)
async def delete_vote(
    request: Request,
    db_session: DBSession,
    review_id: UUID4,
    vote_id: UUID4,
):
    try:
        db_review = review_crud.get(
            request=request, db_session=db_session, id=review_id
        )
        if db_review is None:
            raise ReviewNotFound()

        db_vote = await vote_crud.get(
            request=request, db_session=db_session, id=vote_id
        )
        if db_vote is None:
            return

        await vote_crud.delete(
            request=request, db_session=db_session, db_obj=db_vote, review_id=review_id
        )
        return
    except ReviewNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to update vote {review_id} {vote_id}: {str(e)}")
        raise DetailedHTTPException()
