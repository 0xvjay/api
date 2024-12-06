from datetime import datetime

from pydantic import UUID4, BaseModel

from api.auth.constant import PermissionAction


class AdminLogOutSchema(BaseModel):
    id: UUID4
    user_id: UUID4
    action: PermissionAction
    object: str
    description: str

    created_at: datetime
    updated_at: datetime | None = None


class BaseSiteSettingSchema(BaseModel):
    platform_is_active: bool
    platform_message: str
    admin_panel_is_active: bool
    admin_panel_message: str


class SiteSettingCreateSchema(BaseSiteSettingSchema):
    pass


class SiteSettingUpdateSchema(BaseSiteSettingSchema):
    id: UUID4


class SiteSettingOutSchema(SiteSettingUpdateSchema):
    pass
