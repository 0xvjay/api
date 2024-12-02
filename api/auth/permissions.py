from functools import wraps
from typing import Callable, TypeVar

from fastapi import Request

from api.exceptions import NotAuthenticated, PermissionDenied
from api.user.models import User

from .constant import PermissionAction, PermissionObject

T = TypeVar("T")


def allow_self_access(
    user_id_param: str,
    permission_action: PermissionAction,
    permission_object: PermissionObject,
) -> Callable[[T], T]:
    def decorator(func: T) -> T:
        @wraps(func)
        async def wrapper(*args, request: Request, **kwargs):
            current_user: User = request.state.user
            target_id = kwargs.get(user_id_param)

            if not current_user or current_user.id != target_id:
                if not BasePermissionDependency.has_permission(
                    current_user, permission_action, permission_object
                ):
                    raise PermissionDenied()

            return await func(*args, request=request, **kwargs)

        return wrapper

    return decorator


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

    async def __call__(self, request: Request) -> User:
        """
        FastAPI dependency callable that checks permissions using request.state.user

        Args:
            request: The current request object

        Returns:
            User: The current user if permission check passes

        Raises:
            NotAuthenticated: If no user is authenticated
            PermissionDenied: If user lacks required permission
        """
        current_user = request.state.user
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


class UserAddressPermissions:
    """Permissions for user-address-related actions"""

    create = BasePermissionDependency(
        PermissionAction.CREATE, PermissionObject.USER_ADDRESS
    )
    read = BasePermissionDependency(
        PermissionAction.READ, PermissionObject.USER_ADDRESS
    )
    update = BasePermissionDependency(
        PermissionAction.UPDATE, PermissionObject.USER_ADDRESS
    )
    delete = BasePermissionDependency(
        PermissionAction.DELETE, PermissionObject.USER_ADDRESS
    )
