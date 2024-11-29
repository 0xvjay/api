from fastapi import Depends

from api.exceptions import NotAuthenticated, PermissionDenied
from api.user.models import User

from .constant import PermissionAction, PermissionObject
from .dependencies import get_current_active_user


class BasePermissionDependency:
    """Base class for permission dependencies"""

    def __init__(self, action: PermissionAction, object_name: PermissionObject):
        self.action = action
        self.object_name = object_name

    @staticmethod
    def has_permission(
        user: User, action: PermissionAction, object_name: PermissionObject
    ) -> bool:
        """
        Check if a user has permission to perform an action on an object.

        Args:
            user: The user to check permissions for
            action: The action being performed
            object_name: The object being acted upon

        Returns:
            bool: True if user has permission, False otherwise
        """
        if user is None:
            return False

        if user.is_superuser:
            return True

        return any(
            permission.action == action and permission.object == object_name
            for group in user.groups
            if group.is_active
            for permission in group.permissions
        )

    async def __call__(
        self, current_user: User = Depends(get_current_active_user)
    ) -> User:
        """
        FastAPI dependency callable that checks permissions for the current user

        Args:
            current_user: The current authenticated user

        Returns:
            User: The current user if permission check passes

        Raises:
            NotAuthenticated: If no user is authenticated
            PermissionDenied: If user lacks required permission
        """
        if not current_user:
            raise NotAuthenticated()

        if not self.has_permission(current_user, self.action, self.object_name):
            raise PermissionDenied()

        return current_user


class GroupPermissions:
    """Permissions for group-related actions"""

    create = BasePermissionDependency(PermissionAction.CREATE, PermissionObject.GROUP)
    read = BasePermissionDependency(PermissionAction.READ, PermissionObject.GROUP)
    update = BasePermissionDependency(PermissionAction.UPDATE, PermissionObject.GROUP)
    delete = BasePermissionDependency(PermissionAction.DELETE, PermissionObject.GROUP)


class UserPermissions:
    """Permissions for user-related actions"""

    create = BasePermissionDependency(PermissionAction.CREATE, PermissionObject.USER)
    read = BasePermissionDependency(PermissionAction.READ, PermissionObject.USER)
    update = BasePermissionDependency(PermissionAction.UPDATE, PermissionObject.USER)
    delete = BasePermissionDependency(PermissionAction.DELETE, PermissionObject.USER)


# async def delete_group(group_id: int, current_user: User = Depends(GroupPermissions.delete))
