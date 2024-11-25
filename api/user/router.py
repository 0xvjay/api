import logging
from typing import List

from fastapi import APIRouter, status
from pydantic import UUID4

from api.database import DBSession
from api.exceptions import DetailedHTTPException

from .exceptions import UserEmailOrNameExists, UserNotFound
from .schemas import (
    UserCreateSchema,
    UserOutMinimalSchema,
    UserOutSchema,
    UserUpdateSchema,
)
from .service import create, delete, get, get_by_email_or_username, retrieve, update

router = APIRouter(prefix="/users", tags=["user"])

logger = logging.getLogger(__name__)


@router.post(
    "/", response_model=UserOutMinimalSchema, status_code=status.HTTP_201_CREATED
)
async def add_user(db_session: DBSession, user: UserCreateSchema):
    try:
        db_obj = await get_by_email_or_username(
            db_session=db_session, email=user.email, username=user.username
        )
        if db_obj is not None:
            raise UserEmailOrNameExists()
        result = await create(db_session=db_session, user=user)
        return result
    except UserEmailOrNameExists:
        raise
    except Exception as e:
        logger.exception(f"Failed to create user: {str(e)}")
        raise DetailedHTTPException()


@router.get("/", response_model=List[UserOutMinimalSchema])
async def read_users(
    db_session: DBSession, query_str: str | None = None, order_by: str | None = None
):
    try:
        result = await get(db_session=db_session, query_str=query_str)
        return result
    except Exception as e:
        logger.exception(f"Failed to fetch users: {str(e)}")
        raise DetailedHTTPException()


@router.get("/{user_id}", response_model=UserOutSchema)
async def read_user(db_session: DBSession, user_id: UUID4):
    try:
        result = await retrieve(db_session=db_session, id=user_id)
        if result is None:
            raise UserNotFound()
        return result
    except UserNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to fetch user {user_id}: {str(e)}")
        raise DetailedHTTPException()


@router.put("/{user_id}", response_model=UserOutMinimalSchema)
async def edit_user(db_session: DBSession, user: UserUpdateSchema, user_id: UUID4):
    try:
        db_obj = await get_by_email_or_username(
            db_session=db_session, email=user.email, username=user.username
        )
        if db_obj is not None and user.id != user_id:
            raise UserEmailOrNameExists()
        result = await update(db_session=db_session, user=user, user_id=user_id)
        if result is None:
            raise UserNotFound()
        return result
    except (UserEmailOrNameExists, UserNotFound):
        raise
    except Exception as e:
        logger.exception(f"Failed to update user: {str(e)}")
        raise DetailedHTTPException()


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user(db_session: DBSession, user_id: UUID4):
    try:
        result = await delete(db_session=db_session, id=user_id)
        if not result:
            raise UserNotFound()
        return {"message": "User successfully deleted"}
    except UserNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete user {user_id}: {str(e)}")
        raise DetailedHTTPException()
