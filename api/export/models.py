from sqlalchemy import UUID, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import relationship

from api.models import BaseTimeStamp

from .constant import Status


class Export(BaseTimeStamp):
    __tablename__ = "export_export"

    file = Column(String(255))
    status = Column(Enum(Status), default=Status.CREATED)
    started_at = Column(DateTime(timezone=True))
    finished_at = Column(DateTime(timezone=True))
    user_id = Column(UUID, ForeignKey("user_user.id", ondelete="SET NULL"))

    created_by = relationship("User", backref="exports")
