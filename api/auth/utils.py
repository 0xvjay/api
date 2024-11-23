from datetime import datetime, timedelta
from typing import Any

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import UUID4

from api.config import settings
from api.database import DBSession
from api.exceptions import NotAuthenticated
from api.user.service import get as get_user
from api.user.service import get_by_email as get_user_by_email

from .schemas import JWTSchema

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


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
    user = await get_user_by_email(db_session=db_session, email=email)
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
        user_id: UUID4 = payload.get("sub")
        if id is None:
            raise NotAuthenticated()

        token_data = JWTSchema(id=user_id)
    except InvalidTokenError:
        raise NotAuthenticated()
    user = await get_user(db_session=db_session, id=token_data.id)
    if user is None:
        raise NotAuthenticated()
    return user
