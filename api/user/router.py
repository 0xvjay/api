import logging
from typing import List

from fastapi import APIRouter, Depends, Request, status
from pydantic import UUID4

from api.auth.constant import PermissionAction, PermissionObject
from api.auth.permissions import (
    UserPermissions,
    allow_self_access,
)
from api.database import DBSession
from api.exceptions import DetailedHTTPException

from .exceptions import UserAddressNotFound, UserEmailOrNameExists, UserNotFound
from .schemas import (
    UserAddressCreateSchema,
    UserAddressOutSchema,
    UserAddressUpdateSchema,
    UserCreateSchema,
    UserOutMinimalSchema,
    UserOutSchema,
    UserUpdateSchema,
)
from .service import user_address_crud, user_crud

router = APIRouter(prefix="/users", tags=["user"])

logger = logging.getLogger(__name__)


@router.post(
    "/",
    response_model=UserOutMinimalSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(UserPermissions.create)],
)
async def add_user(db_session: DBSession, user: UserCreateSchema):
    try:
        db_obj = await user_crud.get_by_email_or_username(
            db_session=db_session, email=user.email, username=user.username
        )
        if db_obj is not None:
            raise UserEmailOrNameExists()
        result = await user_crud.create(db_session=db_session, user=user)
        return result
    except UserEmailOrNameExists:
        raise
    except Exception as e:
        logger.exception(f"Failed to create user: {str(e)}")
        raise DetailedHTTPException()


@router.get(
    "/",
    response_model=List[UserOutMinimalSchema],
    dependencies=[Depends(UserPermissions.read)],
)
async def read_users(
    db_session: DBSession, query_str: str | None = None, order_by: str | None = None
):
    try:
        result = await user_crud.list(db_session=db_session, query_str=query_str)
        return result
    except Exception as e:
        logger.exception(f"Failed to fetch users: {str(e)}")
        raise DetailedHTTPException()


@router.get("/{user_id}", response_model=UserOutSchema)
@allow_self_access("user_id", PermissionAction.READ, PermissionObject.USER)
async def read_user(request: Request, db_session: DBSession, user_id: UUID4):
    try:
        result = await user_crud.get(db_session=db_session, id=user_id)
        if result is None:
            raise UserNotFound()
        return result
    except UserNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to fetch user {user_id}: {str(e)}")
        raise DetailedHTTPException()


@router.put("/{user_id}", response_model=UserOutMinimalSchema)
@allow_self_access("user_id", PermissionAction.UPDATE, PermissionObject.USER)
async def edit_user(
    request: Request, db_session: DBSession, user: UserUpdateSchema, user_id: UUID4
):
    try:
        db_user = await user_crud.get(db_session=db_session, id=user_id)
        if db_user is None:
            raise UserNotFound()
        if db_user.email != user.email or db_user.username != user.username:
            db_obj = await user_crud.get_by_email_or_username(
                db_session=db_session, email=user.email, username=user.username
            )
        if db_obj is not None and user.id != user_id:
            raise UserEmailOrNameExists()
        result = await user_crud.update(
            db_session=db_session, user=user, db_user=db_user
        )
        return result
    except (UserEmailOrNameExists, UserNotFound):
        raise
    except Exception as e:
        logger.exception(f"Failed to update user: {str(e)}")
        raise DetailedHTTPException()


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(UserPermissions.delete)],
)
async def remove_user(db_session: DBSession, user_id: UUID4):
    try:
        db_user = await user_crud.get(db_session=db_session, id=user_id)
        if db_user is None:
            raise UserNotFound()
        await user_crud.delete(db_session=db_session, db_obj=db_user)
        return
    except UserNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete user {user_id}: {str(e)}")
        raise DetailedHTTPException()


@router.get("/{user_id}/user_addresses/", response_model=List[UserAddressOutSchema])
@allow_self_access("user_id", PermissionAction.UPDATE, PermissionObject.USER_ADDRESS)
async def read_user_addresses(request: Request, db_session: DBSession, user_id: UUID4):
    try:
        result = await user_address_crud.list(db_session=db_session, user_id=user_id)
        return result
    except Exception as e:
        logger.exception(f"Failed to fetch user addresses of user {user_id}: {str(e)}")
        raise DetailedHTTPException()


@router.get(
    "/{user_id}/user_addresses/{user_address_id}",
    response_model=UserAddressOutSchema,
)
@allow_self_access("user_id", PermissionAction.UPDATE, PermissionObject.USER_ADDRESS)
async def read_user_address(
    request: Request, db_session: DBSession, user_id: UUID4, user_address_id: UUID4
):
    try:
        result = await user_address_crud.get(
            db_session=db_session, id=user_address_id, user_id=user_id
        )
        if result is None:
            raise UserAddressNotFound()
        return result
    except UserAddressNotFound:
        raise
    except Exception as e:
        logger.exception(
            f"Failed to fetch user address {user_address_id} of user {user_id}: {str(e)}"
        )
        raise DetailedHTTPException()


@router.post(
    "/{user_id}/user_addresses/",
    response_model=UserAddressOutSchema,
    status_code=status.HTTP_201_CREATED,
)
@allow_self_access("user_id", PermissionAction.UPDATE, PermissionObject.USER_ADDRESS)
async def add_user_address(
    request: Request,
    db_session: DBSession,
    user_address: UserAddressCreateSchema,
    user_id: UUID4,
):
    try:
        result = await user_address_crud.create(
            db_session=db_session, schema=user_address, user_id=user_id
        )
        return result
    except Exception as e:
        logger.exception(f"Failed to create user address of user {user_id}: {str(e)}")
        raise DetailedHTTPException()


@router.put(
    "/{user_id}/user_addresses/{user_address_id}", response_model=UserAddressOutSchema
)
@allow_self_access("user_id", PermissionAction.UPDATE, PermissionObject.USER_ADDRESS)
async def edit_user_address(
    request: Request,
    db_session: DBSession,
    user_address: UserAddressUpdateSchema,
    user_id: UUID4,
    user_address_id: UUID4,
):
    try:
        db_user_address = await user_address_crud.get(
            db_session=db_session, id=user_address_id, user_id=user_id
        )
        if db_user_address is None:
            raise UserAddressNotFound()
        updated_user_address = await user_address_crud.update(
            db_session=db_session, db_obj=db_user_address, schema=user_address
        )
        return updated_user_address
    except UserAddressNotFound:
        raise
    except Exception as e:
        logger.exception(
            f"Failed to update user address {user_address_id} of user {user_id}: {str(e)}"
        )
        raise DetailedHTTPException()


@router.delete(
    "/{user_id}/user_addresses/{user_address_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@allow_self_access("user_id", PermissionAction.UPDATE, PermissionObject.USER_ADDRESS)
async def remove_user_address(
    request: Request, db_session: DBSession, user_id: UUID4, user_address_id: UUID4
):
    try:
        db_user_address = await user_address_crud.get(
            db_session=db_session, id=user_address_id, user_id=user_id
        )
        if db_user_address is None:
            raise UserAddressNotFound()
        await user_address_crud.delete(db_session=db_session, db_obj=db_user_address)
        return
    except Exception as e:
        logger.exception(
            f"Failed to delete user address {user_address_id} of user {user_id}: {str(e)}"
        )
        raise DetailedHTTPException()
