import uuid

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from api.database import Base


class BaseUUID(Base):
    __abstract__ = True

    id = Column(UUID, primary_key=True, default=uuid.uuid4)


class BaseTimeStamp(BaseUUID):
    __abstract__ = True

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
