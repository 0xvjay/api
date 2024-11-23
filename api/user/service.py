from pydantic import UUID4, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User


async def get(db_session: AsyncSession, id: UUID4) -> User | None:
    result = await db_session.execute(select(User).where(User.id == id))
    return result.scalar_one_or_none()


async def get_by_email(db_session: AsyncSession, email: EmailStr) -> User | None:
    result = await db_session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()
