import logging
from typing import List

from fastapi import APIRouter, Depends, Request

from api.auth.permissions import AdminLogPermissions, SiteSettingPermissions
from api.database import DBSession
from api.exceptions import DetailedHTTPException

from .schemas import AdminLogOutSchema, SiteSettingOutSchema, SiteSettingUpdateSchema
from .service import admin_log_crud, site_setting_crud

logger = logging.getLogger(__name__)

router = APIRouter(tags=["logs"])


@router.get(
    "/logs/",
    response_model=List[AdminLogOutSchema],
    dependencies=[Depends(AdminLogPermissions.read)],
)
async def read_logs(
    request: Request,
    db_session: DBSession,
    query_str: str | None = None,
    order_by: str | None = None,
):
    try:
        result = await admin_log_crud.list(
            db_session=db_session,
            request=request,
            query_str=query_str,
            order_by=order_by,
        )
        return result
    except Exception as e:
        logger.exception(f"Failed to fetch admin logs: {str(e)}")
        raise DetailedHTTPException()


@router.get(
    "/site_settings/",
    response_model=SiteSettingOutSchema,
    dependencies=[Depends(SiteSettingPermissions.read)],
)
async def read_site_settings(request: Request, db_session: DBSession):
    try:
        result = await site_setting_crud.get(request=request, db_session=db_session)
        return result
    except Exception as e:
        logger.exception(f"Failed to fetch site settings: {str(e)}")
        raise DetailedHTTPException()


@router.put(
    "/site_settings/",
    response_model=SiteSettingOutSchema,
    dependencies=[Depends(SiteSettingPermissions.update)],
)
async def edit_site_settings(
    request: Request, db_session: DBSession, site_setting: SiteSettingUpdateSchema
):
    try:
        result = await site_setting_crud.update(
            request=request, db_session=db_session, site_setting=site_setting
        )
        return result
    except Exception as e:
        logger.exception(f"Failed to update site settings: {str(e)}")
        raise DetailedHTTPException()
