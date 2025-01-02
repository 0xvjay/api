from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.crud import CRUDBase

from .models import Voucher
from .schemas import VoucherCreateSchema, VoucherUpdateSchema


class CRUDVoucher(CRUDBase[Voucher, VoucherCreateSchema, VoucherUpdateSchema]):
    async def get_by_name_or_code(
        self, db_session: AsyncSession, name: str | None = None, code: str | None = None
    ) -> Voucher:
        query = select(Voucher)
        conditions = []

        if name:
            conditions.append(Voucher.name == name)
        if code:
            conditions.append(Voucher.code == code)

        query = query.where(or_(*conditions))

        result = await db_session.execute(query)
        return result.scalar_one_or_none()


voucher_crud = CRUDVoucher(Voucher, "Voucher")
