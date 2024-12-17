from dataclasses import dataclass
from decimal import Decimal
from typing import List

from fastapi import Request
from pydantic import UUID4
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api.core.crud import CRUDBase
from api.user.models import Credit, ProductLimit, Project, Transaction, User

from .constant import OrderStatus
from .exceptions import InsufficientCredit
from .models import Order, OrderLine
from .schemas import OrderCreateSchema, OrderUpdateSchema


@dataclass
class ProjectCredit:
    project_id: UUID4
    available_amount: Decimal
    absolute_limit: bool
    product_id: UUID4 | None = None


class CRUDOrder(CRUDBase[Order, OrderCreateSchema, OrderUpdateSchema]):
    async def get_user_project_credits(
        self, db_session: AsyncSession, user_id: UUID4, product_ids: List[UUID4]
    ) -> List[ProjectCredit]:
        query = (
            select(Credit, ProductLimit)
            .join(Project, Credit.project_id == Project.id)
            .outerjoin(
                ProductLimit,
                and_(
                    ProductLimit.project_id == Project.id,
                    ProductLimit.product_id.in_(product_ids),
                ),
            )
            .where(Credit.user_id == user_id)
        )
        result = await db_session.execute(query)

        project_credits: List[ProjectCredit] = []
        for credit, product_limit in result:
            project_credits.append(
                ProjectCredit(
                    project_id=credit.project_id,
                    available_amount=credit.amount,
                    absolute_limit=product_limit.absolute_limit
                    if product_limit
                    else False,
                    product_id=product_limit.product_id if product_limit else None,
                )
            )

        return sorted(
            project_credits,
            key=lambda x: (x.absolute_limit, x.available_amount),
            reverse=True,
        )

    async def get(
        self, request: Request, db_session: AsyncSession, id: UUID4
    ) -> Order | None:
        await self._create_get_log(request=request, db_session=db_session, id=id)
        result = await db_session.execute(
            select(Order)
            .where(Order.id == id)
            .options(joinedload(Order.user))
            .options(
                joinedload(Order.lines).joinedload(OrderLine.product),
            )
        )
        return result.unique().scalar_one_or_none()

    async def create(
        self, request: Request, db_session: AsyncSession, order: OrderCreateSchema
    ) -> Order:
        await self._create_add_log(request=request, db_session=db_session)
        user: User = request.state.user

        product_ids = [line.product.id for line in order.lines]

        project_credits = await self.get_user_project_credits(
            db_session, user.id, product_ids
        )

        db_order = Order(
            user_id=user.id,
            guest_email=order.guest_email,
            total_excl_tax=Decimal(0),
            total_incl_tax=Decimal(0),
            status=OrderStatus.INIT,
        )
        db_session.add(db_order)
        await db_session.flush()

        order_lines = []
        transactions = []

        for line in order.lines:
            amount_needed = line.product.price * line.quantity
            amount_covered = Decimal(0)

            for credit in project_credits:
                if amount_covered >= amount_needed:
                    break

                if credit.product_id == line.product.id:
                    available = min(
                        credit.available_amount, amount_needed - amount_covered
                    )
                    if available > 0:
                        transactions.append(
                            Transaction(
                                credit_id=credit.project_id,
                                order_id=db_order.id,
                                amount=available,
                            )
                        )
                        amount_covered += available
                        credit.available_amount -= available

            if amount_covered < amount_needed:
                for credit in project_credits:
                    if amount_covered >= amount_needed:
                        break

                    if credit.product_id is None:
                        available = min(
                            credit.available_amount, amount_needed - amount_covered
                        )
                        if available > 0:
                            transactions.append(
                                Transaction(
                                    credit_id=credit.project_id,
                                    order_id=db_order.id,
                                    amount=available,
                                )
                            )
                            amount_covered += available
                            credit.available_amount -= available

            if amount_covered < amount_needed:
                await db_session.rollback()
                raise InsufficientCredit()

            db_order_line = OrderLine(
                order_id=db_order.id,
                product_id=line.product.id,
                quantity=line.quantity,
                unit_price_excl_tax=line.product.price,
                unit_price_incl_tax=line.product.price,
                line_price_excl_tax=amount_needed,
                line_price_incl_tax=amount_needed,
                line_price_before_discounts_excl_tax=amount_needed,
                line_price_before_discounts_incl_tax=amount_needed,
            )
            order_lines.append(db_order_line)
            db_order.total_excl_tax += amount_needed
            db_order.total_incl_tax += amount_needed

        db_session.add_all(order_lines)
        db_session.add_all(transactions)

        await db_session.commit()
        await db_session.refresh(db_order)

        return db_order

    async def update(
        self,
        request: Request,
        db_session: AsyncSession,
        db_order: Order,
        order: OrderUpdateSchema,
    ) -> Order:
        await self._create_update_log(request=request, db_session=db_session)
        if order.guest_email is not None:
            db_order.guest_email = order.guest_email

        db_order.status = order.status

        await db_session.commit()
        await db_session.refresh(db_order)
        return db_order

    async def get_user_orders(
        self, request: Request, db_session: AsyncSession, user_id: UUID4
    ) -> List[Order]:
        await self._create_list_log(request=request, db_session=db_session)
        result = await db_session.execute(select(Order).where(Order.user_id == user_id))
        return result


order_crud = CRUDOrder(Order, "Order")
