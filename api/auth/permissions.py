from abc import ABC, abstractmethod
from typing import List

from fastapi import Depends
from sqlalchemy.orm import Session

from api.auth.models import Group
from api.database import get_db
from api.exceptions import NotAuthenticated, PermissionDenied
from api.user.models import User

from .constant import PermissionAction, PermissionObject
from .dependencies import get_current_active_user


class PermissionChecker:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def has_permission(
        self, user: User, action: PermissionAction, object_name: str
    ) -> bool:
        user_groups: List[Group] = user.groups

        if user.is_superuser:
            return True

        return any(
            group.is_active
            and any(
                permission.action == action and permission.object == object_name
                for permission in group.permissions
            )
            for group in user_groups
        )


class BasePermission(ABC):
    def __init__(
        self,
        db_session: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
    ):
        self.db_session = db_session
        self.user = current_user
        self.permission_checker = PermissionChecker(self.db_session)

        if not self.user:
            raise NotAuthenticated()

        if not self.has_required_permissions():
            raise PermissionDenied()

    @abstractmethod
    def has_required_permissions(self) -> bool: ...


class ObjectPermission(BasePermission):
    def __init__(
        self,
        required_action: PermissionAction,
        object_name: str,
        db_session: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
    ):
        self.required_action = required_action
        self.object_name = object_name
        super().__init__(db_session=db_session, current_user=current_user)

    def has_required_permissions(self) -> bool:
        return self.permission_checker.has_permission(
            self.user, self.required_action, self.object_name
        )


class GroupReadPermission(ObjectPermission):
    def __init__(
        self,
        db_session=Depends(get_db),
        current_user=Depends(get_current_active_user),
    ):
        super().__init__(
            PermissionAction.READ,
            PermissionObject.GROUP,
            db_session=db_session,
            current_user=current_user,
        )
