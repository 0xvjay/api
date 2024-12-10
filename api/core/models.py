from sqlalchemy import UUID, Boolean, Column, Enum, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from api.models import BaseTimeStamp, BaseUUID

from .constant import Action


class AdminLog(BaseTimeStamp):
    __tablename__ = "core_admin_log"

    user_id = Column(UUID, ForeignKey("user_user.id", ondelete="SET NULL"))
    action = Column(Enum(Action))
    object = Column(String(255))
    description = Column(Text)

    user = relationship("User", backref="admin_logs")


class SiteSetting(BaseUUID):
    __tablename__ = "core_site_setting"

    platform_is_active = Column(Boolean, default=True)
    platform_message = Column(Text)
    admin_panel_is_active = Column(Boolean, default=True)
    admin_panel_message = Column(Text)
