from fastapi import Depends

from api.database import DBSession

from ..constant import PermissionAction, PermissionObject
from ..dependencies import get_current_active_user
from .base import ObjectPermission


class GroupReadPermission(ObjectPermission):
    def __init__(
        self,
        db_session=DBSession,
        current_user=Depends(get_current_active_user),
    ):
        super().__init__(
            PermissionAction.READ,
            PermissionObject.GROUP,
            db_session=db_session,
            current_user=current_user,
        )


class GroupCreatePermission(ObjectPermission):
    def __init__(
        self,
        db_session=DBSession,
        current_user=Depends(get_current_active_user),
    ):
        super().__init__(
            PermissionAction.CREATE,
            PermissionObject.GROUP,
            db_session=db_session,
            current_user=current_user,
        )


class GroupUpdatePermission(ObjectPermission):
    def __init__(
        self,
        db_session=DBSession,
        current_user=Depends(get_current_active_user),
    ):
        super().__init__(
            PermissionAction.UPDATE,
            PermissionObject.GROUP,
            db_session=db_session,
            current_user=current_user,
        )


class GroupDeletePermission(ObjectPermission):
    def __init__(
        self,
        db_session=DBSession,
        current_user=Depends(get_current_active_user),
    ):
        super().__init__(
            PermissionAction.DELETE,
            PermissionObject.GROUP,
            db_session=db_session,
            current_user=current_user,
        )
