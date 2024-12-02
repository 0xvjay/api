from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.services.crud import CRUDBase

from .models import AdminLog, SiteSetting
from .schemas import (
    AdminLogCreateSchema,
    AdminLogUpdateSchema,
    SiteSettingCreateSchema,
    SiteSettingUpdateSchema,
)


class CRUDAdminLog(CRUDBase[AdminLog, AdminLogCreateSchema, AdminLogUpdateSchema]):
    async def create(self, db_session: AsyncSession, admin_log: AdminLogCreateSchema):
        db_obj = AdminLog(**admin_log.model_dump())
        db_session.add(db_obj)

        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj


class CRUDSiteSetting(
    CRUDBase[SiteSetting, SiteSettingCreateSchema, SiteSettingUpdateSchema]
):
    async def get(self, db_session: AsyncSession) -> SiteSetting:
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
        self, db_session: AsyncSession, site_setting: SiteSettingUpdateSchema
    ):
        result = await db_session.execute(select(SiteSetting))
        db_site_setting = result.scalar_one_or_none()

        if db_site_setting is None:
            db_site_setting = await self.get(db_session=db_session)

        for field, value in site_setting.model_dump(exclude_unset=True).items():
            setattr(site_setting, field, value)

        db_session.add(site_setting)
        await db_session.commit()
        await db_session.refresh(site_setting)

        return site_setting


admin_log_crud = CRUDAdminLog(AdminLog)
site_setting_crud = CRUDSiteSetting(SiteSetting)
