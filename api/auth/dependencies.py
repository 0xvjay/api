from fastapi import Depends, Request

from api.user.models import User

from .exceptions import InactiveUser
from .utils import get_current_user


async def get_current_active_user(
    request: Request, current_user: User = Depends(get_current_user)
):
    if not current_user.is_active:
        raise InactiveUser()
    request.state.user = current_user
    return current_user
