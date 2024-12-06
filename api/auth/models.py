from sqlalchemy import UUID, Boolean, Column, ForeignKey, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from api.models import BaseTimeStamp, BaseUUID

from .constant import PermissionAction


class UserGroup(BaseUUID):
    __tablename__ = "auth_user_group"

    group_id = Column(
        UUID,
        ForeignKey("auth_group.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id = Column(
        UUID,
        ForeignKey("user_user.id", ondelete="CASCADE"),
        primary_key=True,
    )


class GroupPermission(BaseUUID):
    __tablename__ = "auth_group_permission"

    group_id = Column(
        UUID,
        ForeignKey("auth_group.id", ondelete="CASCADE"),
        primary_key=True,
    )
    permission_id = Column(
        UUID,
        ForeignKey("auth_permission.id", ondelete="CASCADE"),
        primary_key=True,
    )


class Group(BaseTimeStamp):
    __tablename__ = "auth_group"

    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)

    permissions = relationship(
        "Permission",
        secondary="auth_group_permission",
        back_populates="groups",
        lazy="joined",
    )
    users = relationship("User", secondary="auth_user_group", back_populates="groups")


class Permission(BaseTimeStamp):
    __tablename__ = "auth_permission"

    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text)
    action = Column(SQLEnum(PermissionAction), nullable=False)
    object = Column(String(255), nullable=False)

    groups = relationship(
        "Group",
        secondary="auth_group_permission",
        back_populates="permissions",
    )
