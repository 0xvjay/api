from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Permission


async def get(db_session: AsyncSession) -> List[Permission]:
    result = await db_session.execute(select(Permission))
    return result.scalars().all()
