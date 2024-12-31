import logging
from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, Request, status
from pydantic import UUID4

from api.config import settings
from api.database import DBSession
from api.exceptions import DetailedHTTPException
from api.user.exceptions import UserNotFound

from .exceptions import GroupExists, GroupNotFound
from .permissions import GroupPermissions
from .schemas import (
    AuthSchema,
    GroupCreateSchema,
    GroupOutMinimalSchema,
    GroupOutSchema,
    GroupUpdateSchema,
    PermissionOutMinimalSchema,
    TokenSchema,
)
from .service import get_permissions, group_crud
from .utils import authenticate_user, create_access_token, create_refresh_token

router = APIRouter(tags=["groups"])
logger = logging.getLogger(__name__)


not_authenticated_router = APIRouter()


@not_authenticated_router.post("/login")
async def login(
    db_session: DBSession,
    form: AuthSchema,
) -> TokenSchema:
    try:
        user = await authenticate_user(
            db_session=db_session, email=form.email, password=form.password
        )
        if not user:
            raise UserNotFound()
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(user.id, expires_delta=access_token_expires)
        refresh_token = create_refresh_token(
            user.id, expires_delta=refresh_token_expires
        )

        return TokenSchema(access_token=access_token, refresh_token=refresh_token)
    except UserNotFound:
        raise
    except Exception as e:
        logger.exception(f"Login failed: {str(e)}")
        raise DetailedHTTPException()


@router.get(
    "/groups/",
    response_model=List[GroupOutMinimalSchema],
    dependencies=[Depends(GroupPermissions.read)],
)
async def read_groups(
    request: Request,
    db_session: DBSession,
    query_str: str | None = None,
    order_by: str | None = None,
):
    try:
        result = await group_crud.list(
            request=request,
            db_session=db_session,
            query_str=query_str,
            order_by=order_by,
        )
        return result
    except Exception as e:
        logger.exception(f"Failed to fetch groups: {str(e)}")
        raise DetailedHTTPException()


@router.get(
    "/groups/{group_id}",
    response_model=GroupOutSchema,
    dependencies=[Depends(GroupPermissions.read)],
)
async def read_group(request: Request, db_session: DBSession, group_id: UUID4):
    try:
        result = await group_crud.get(
            request=request, db_session=db_session, id=group_id
        )
        if result is None:
            raise GroupNotFound()
        return result
    except GroupNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to fetch group {group_id}: {str(e)}")
        raise DetailedHTTPException()


@router.post(
    "/groups/",
    response_model=GroupOutMinimalSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(GroupPermissions.create)],
)
async def add_group(request: Request, db_session: DBSession, group: GroupCreateSchema):
    try:
        db_obj = await group_crud.get_by_name(db_session=db_session, name=group.name)
        if db_obj is not None:
            raise GroupExists()
        result = await group_crud.create(
            request=request, db_session=db_session, group=group
        )
        return result
    except GroupExists:
        raise
    except Exception as e:
        logger.exception(f"Failed to create group: {str(e)}")
        raise DetailedHTTPException()


@router.put(
    "/groups/{group_id}",
    response_model=GroupOutMinimalSchema,
    dependencies=[Depends(GroupPermissions.update)],
)
async def edit_group(
    request: Request, db_session: DBSession, group: GroupUpdateSchema, group_id: UUID4
):
    try:
        db_group = await group_crud.get(
            request=request, db_session=db_session, id=group_id
        )
        if db_group is None:
            raise GroupNotFound()
        if db_group != group.name:
            existing_group = await group_crud.get_by_name(
                db_session=db_session, name=group.name
            )
            if existing_group is not None and existing_group.id != group_id:
                raise GroupExists()
        updated_group = await group_crud.update(
            request=request, db_session=db_session, group=group, db_group=db_group
        )
        return updated_group
    except (GroupExists, GroupNotFound):
        raise
    except Exception as e:
        logger.exception(f"Failed to update group: {str(e)}")
        raise DetailedHTTPException()


@router.delete(
    "/groups/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(GroupPermissions.delete)],
)
async def remove_group(request: Request, db_session: DBSession, group_id: UUID4):
    try:
        db_group = await group_crud.get(
            request=request, db_session=db_session, id=group_id
        )
        if db_group is None:
            raise GroupNotFound()
        await group_crud.delete(request=request, db_session=db_session, db_obj=db_group)
        return
    except GroupNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete group {group_id}: {str(e)}")
        raise DetailedHTTPException()


@router.get(
    "/permissions/",
    response_model=List[PermissionOutMinimalSchema],
    dependencies=[Depends(GroupPermissions.read)],
)
async def read_permissions(db_session: DBSession):
    try:
        result = await get_permissions(db_session=db_session)
        return result
    except Exception as e:
        logger.exception(f"Failed to fetch permissions: {str(e)}")
        raise DetailedHTTPException()
