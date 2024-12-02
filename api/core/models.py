from sqlalchemy import UUID, Boolean, Column, Enum, ForeignKey, String, Text

from api.auth.constant import PermissionAction
from api.models import BaseTimeStamp, BaseUUID


class AdminLog(BaseTimeStamp):
    __tablename__ = "core_admin_log"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("user_user.id", ondelete="SET NULL")
    )
    action = Column(Enum(PermissionAction))
    object = Column(String(255))
    description = Column(Text)


class SiteSetting(BaseUUID):
    __tablename__ = "core_site_setting"

    platform_is_active = Column(Boolean, default=True)
    platform_message = Column(Text)
    admin_panel_is_active = Column(Boolean, default=True)
    admin_panel_message = Column(Text)
