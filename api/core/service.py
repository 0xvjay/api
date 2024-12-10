from typing import Any

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.crud import CRUDBase

from .models import AdminLog, SiteSetting
from .schemas import (
    SiteSettingCreateSchema,
    SiteSettingUpdateSchema,
)


class CRUDAdminLog(CRUDBase[AdminLog, Any, Any]):
    pass


class CRUDSiteSetting(
    CRUDBase[SiteSetting, SiteSettingCreateSchema, SiteSettingUpdateSchema]
):
    async def get(self, request: Request, db_session: AsyncSession) -> SiteSetting:
        await self._create_list_log(request=request, db_session=db_session)
        result = await db_session.execute(select(SiteSetting))
        db_site_setting = result.scalar_one_or_none()

        if db_site_setting is None:
            db_site_setting = SiteSetting(
                platform_is_active=True,
                platform_message="",
                admin_panel_is_active=True,
                admin_panel_message="",
            )
            db_session.add(db_site_setting)

            await db_session.commit()
            await db_session.refresh(db_site_setting)

        return db_site_setting

    async def update(
        self,
        request: Request,
        db_session: AsyncSession,
        site_setting: SiteSettingUpdateSchema,
    ):
        await self._create_update_log(request=request, db_session=db_session)
        result = await db_session.execute(select(SiteSetting))
        db_site_setting = result.scalar_one_or_none()

        if db_site_setting is None:
            db_site_setting = await self.get(db_session=db_session)

        for field, value in site_setting.model_dump(exclude_unset=True).items():
            setattr(db_site_setting, field, value)

        db_session.add(db_site_setting)
        await db_session.commit()
        await db_session.refresh(db_site_setting)

        return db_site_setting


admin_log_crud = CRUDAdminLog(AdminLog, "Admin Log")
site_setting_crud = CRUDSiteSetting(SiteSetting, "Site Setting")
