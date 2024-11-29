from decimal import Decimal

from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api.service import CRUDBase

from .constant import OrderStatus
from .models import Order, OrderLine
from .schemas import OrderCreateSchema, OrderUpdateSchema


class CRUDOrder(CRUDBase[Order, OrderCreateSchema, OrderUpdateSchema]):
    async def get(self, db_session: AsyncSession, id: UUID4) -> Order | None:
        result = await db_session.execute(
            select(Order)
            .where(Order.id == id)
            .options(joinedload(Order.user))
            .options(
                joinedload(Order.lines).joinedload(OrderLine.product),
            )
        )
        return result.unique().scalar_one_or_none()

    async def create(self, db_session: AsyncSession, order: OrderCreateSchema) -> Order:
        total_excl_tax = Decimal(0)
        total_incl_tax = Decimal(0)

        db_order = Order(
            guest_email=order.guest_email,
            total_excl_tax=total_excl_tax,
            total_incl_tax=total_incl_tax,
            status=OrderStatus.INIT,
        )
        db_session.add(db_order)
        await db_session.flush()

        order_lines = []
        for line in order.lines:
            unit_price_excl_tax = line.product.price
            unit_price_incl_tax = line.product.price

            line_price_excl_tax = unit_price_excl_tax * line.quantity
            line_price_incl_tax = unit_price_incl_tax * line.quantity

            db_order_line = OrderLine(
                order_id=db_order.id,
                product_id=line.product.id,
                quantity=line.quantity,
                unit_price_excl_tax=unit_price_excl_tax,
                unit_price_incl_tax=unit_price_incl_tax,
                line_price_excl_tax=line_price_excl_tax,
                line_price_incl_tax=line_price_incl_tax,
                line_price_before_discounts_excl_tax=line_price_excl_tax,
                line_price_before_discounts_incl_tax=line_price_incl_tax,
            )
            order_lines.append(db_order_line)

            total_excl_tax += line_price_excl_tax
            total_incl_tax += line_price_incl_tax

        db_order.total_excl_tax = total_excl_tax
        db_order.total_incl_tax = total_incl_tax

        db_session.add_all(order_lines)
        await db_session.commit()
        await db_session.refresh(db_order)

        return db_order

    async def update(
        self, db_session: AsyncSession, db_order: Order, order: OrderUpdateSchema
    ) -> Order:
        if order.guest_email is not None:
            db_order.guest_email = order.guest_email

        db_order.status = order.status

        await db_session.commit()
        await db_session.refresh(db_order)
        return db_order


order_crud = CRUDOrder(Order)
