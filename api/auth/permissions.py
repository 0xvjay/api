from abc import ABC, abstractmethod
from fastapi import Request


class BasePermission(ABC):
    """
    Abstract permission that all other Permissions must be inherited from.

    Defines basic error message, status & error codes.

    Upon initialization, calls abstract method  `has_required_permissions`
    which will be specific to concrete implementation of Permission class.

    You would write your permissions like this:

    >>> class TeapotUserAgentPermission(BasePermission):

    >>>     def has_required_permissions(self, request: Request) -> bool:
    >>>         return request.headers.get('User-Agent') == "Teapot v1.0"

    """

    @abstractmethod
    def has_required_permissions(self, request: Request) -> bool: ...

    def __init__(self, request: Request):
        pass
