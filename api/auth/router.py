import logging
from datetime import timedelta

from fastapi import APIRouter

from api.config import settings
from api.database import DBSession
from api.exceptions import DetailedHTTPException

from .exceptions import UserNotFoundError
from .schemas import AuthSchema, TokenSchema
from .utils import authenticate_user, create_access_token, create_refresh_token

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/login")
async def login(
    db_session: DBSession,
    form: AuthSchema,
) -> TokenSchema:
    try:
        user = await authenticate_user(
            db_session=db_session, email=form.email, password=form.password
        )
        if not user:
            raise UserNotFoundError()
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(user.id, expires_delta=access_token_expires)
        refresh_token = create_refresh_token(
            user.id, expires_delta=refresh_token_expires
        )

        return TokenSchema(access_token=access_token, refresh_token=refresh_token)
    except Exception as e:
        logger.exception(e)
        raise DetailedHTTPException()


@router.get("groups/")
async def read_groups(db_session: DBSession):
    pass
