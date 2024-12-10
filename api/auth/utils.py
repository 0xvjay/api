from datetime import datetime, timedelta
from typing import Any

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from api.config import settings
from api.database import DBSession
from api.exceptions import NotAuthenticated
from api.user.models import User
from api.user.service import user_crud

from .models import Group
from .schemas import JWTSchema
from .security import verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(subject: str | Any, expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.now() + expires_delta
    else:
        expires_delta = datetime.now() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: str | Any, expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.now() + expires_delta
    else:
        expires_delta = datetime.now() + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_REFRESH_SECRET_KEY, settings.ALGORITHM
    )
    return encoded_jwt


async def authenticate_user(db_session: DBSession, email: str, password: str):
    user = await user_crud.get_by_email_or_username(db_session=db_session, email=email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


async def get_current_user(db_session: DBSession, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise NotAuthenticated()

        token_data = JWTSchema(sub=user_id)
    except InvalidTokenError:
        raise NotAuthenticated()
    result = await db_session.execute(
        select(User)
        .options(joinedload(User.groups).joinedload(Group.permissions))
        .where(User.id == token_data.id)
    )
    user = result.unique().scalar_one_or_none()
    if user is None:
        raise NotAuthenticated()
    return user
