from fastapi import Depends

from api.user.models import User

from .exceptions import InactiveUser
from .utils import get_current_user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise InactiveUser()
    return current_user
