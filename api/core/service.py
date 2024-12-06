import logging
from typing import Any

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.crud import CRUDBase

from .constant import Action
from .models import AdminLog, SiteSetting
from .schemas import (
    SiteSettingCreateSchema,
    SiteSettingUpdateSchema,
)

logger = logging.getLogger(__name__)


async def create_admin_log(
    db_session: AsyncSession,
    user_id: UUID4,
    action: Action,
    object_name: str,
    description: str | None = None,
) -> None:
    """
    Create an admin log entry to track administrative actions.

    Args:
        db_session: Database session
        user_id: UUID of the user performing the action
        action: Type of action performed (from Action enum)
        object_name: Name/identifier of the object being acted upon
        description: Optional detailed description of the action

    """
    try:
        admin_log = AdminLog(
            user_id=user_id, action=action, object=object_name, description=description
        )

        db_session.add(admin_log)
        await db_session.commit()
        await db_session.refresh(admin_log)

        return

    except Exception as e:
        await db_session.rollback()
        logger.exception(
            f"Failed to create admin log: {str(e)}, {user_id} {action} {object_name}"
        )


class CRUDAdminLog(CRUDBase[AdminLog, Any, Any]):
    pass


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
            setattr(db_site_setting, field, value)

        db_session.add(db_site_setting)
        await db_session.commit()
        await db_session.refresh(db_site_setting)

        return db_site_setting


admin_log_crud = CRUDAdminLog(AdminLog, "Admin Log")
site_setting_crud = CRUDSiteSetting(SiteSetting, "Site Setting")
