import logging
from datetime import timedelta
from typing import List

from fastapi import APIRouter
from pydantic import UUID4

from api.config import settings
from api.database import DBSession
from api.exceptions import DetailedHTTPException
from api.user.exceptions import UserNotFound

from .exceptions import GroupExists
from .schemas import (
    AuthSchema,
    GroupCreateSchema,
    GroupOutMinimalSchema,
    GroupOutSchema,
    GroupUpdateSchema,
    TokenSchema,
)
from .service.group import (
    create as create_group,
)
from .service.group import (
    delete as delete_group,
)
from .service.group import (
    get as get_groups,
)
from .service.group import (
    get_by_name as get_group_by_name,
)
from .service.group import (
    retrieve as retrieve_group,
)
from .service.group import (
    update as update_group,
)
from .utils import authenticate_user, create_access_token, create_refresh_token

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/login")
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
    except Exception as e:
        logger.exception(e)
        raise DetailedHTTPException()


@router.get("/groups/", response_model=List[GroupOutMinimalSchema])
async def read_groups(
    db_session: DBSession,
    query_str: str | None = None,
    order_by: str | None = None,
):
    result = await get_groups(
        db_session=db_session, query_str=query_str, order_by=order_by
    )
    return result


@router.get("/groups/{group_id}", response_model=GroupOutSchema)
async def read_group(db_session: DBSession, group_id: UUID4):
    result = await retrieve_group(db_session=db_session, id=group_id)
    return result


@router.post("/groups/", response_model=GroupOutMinimalSchema)
async def add_group(db_session: DBSession, group: GroupCreateSchema):
    db_obj = get_group_by_name(db_session=db_session, name=group.name)
    if db_obj is not None:
        raise GroupExists()
    result = await create_group(db_session=db_session, group=group)
    return result


@router.put("/groups/{group_id}", response_model=GroupOutMinimalSchema)
async def edit_group(db_session: DBSession, group: GroupUpdateSchema):
    db_obj = get_group_by_name(db_session=db_session, name=group.name)
    if db_obj is not None:
        raise GroupExists()
    result = await update_group(db_session=db_session, group=group)
    return result


@router.delete("/groups/{group_id}")
async def remove_group(db_session: DBSession, group_id: UUID4):
    result = await delete_group(db_session=db_session, id=group_id)
    return result
