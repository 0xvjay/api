from typing import Any

from fastapi import HTTPException, status


class DetailedHTTPException(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Server Error"

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        super().__init__(status_code=self.status_code, detail=self.detail, **kwargs)


class PermissionDenied(DetailedHTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Permission denied"


class NotFound(DetailedHTTPException):
    status_code = status.HTTP_404_NOT_FOUND


class BadRequest(DetailedHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Bad Request"


class NotAuthenticated(DetailedHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "User not authenticated"

    def __init__(self) -> None:
        super().__init__(headers={"WWW-Authenticate": "Bearer"})
