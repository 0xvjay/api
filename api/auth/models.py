from enum import StrEnum

from sqlalchemy import UUID, Boolean, Column, ForeignKey, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from api.models import BaseTimeStamp, BaseUUID


class PermissionAction(StrEnum):
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class GroupPermission(BaseUUID):
    __tablename__ = "auth_group_permission"

    group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("auth_group.id", ondelete="CASCADE"),
        primary_key=True,
    )
    permission_id = Column(
        UUID(as_uuid=True),
        ForeignKey("auth_permission.id", ondelete="CASCADE"),
        primary_key=True,
    )


class Group(BaseTimeStamp):
    __tablename__ = "auth_group"

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)

    permissions = relationship(
        "Permission",
        secondary="auth_group_permission",
        backref="groups",
        viewonly=True,
    )


class Permission(BaseTimeStamp):
    __tablename__ = "auth_permission"

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text)
    action = Column(SQLEnum(PermissionAction), nullable=False)
    object = Column(String(255), nullable=False)

    groups = relationship(
        "Group",
        secondary="auth_group_permission",
        backref="permissions",
        viewonly=True,
    )
