import logging
from typing import List

from fastapi import APIRouter
from pydantic import UUID4

from api.database import DBSession
from api.exceptions import DetailedHTTPException

from .exceptions import OrderNotFound
from .schemas import (
    OrderCreateSchema,
    OrderOutMinimalSchema,
    OrderOutSchema,
    OrderUpdateSchema,
)
from .service import order_crud

router = APIRouter(prefix="/orders", tags=["order"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[OrderOutMinimalSchema])
async def read_orders(
    db_session: DBSession, query_str: str | None = None, order_by: str | None = None
):
    try:
        result = await order_crud.list(
            db_session=db_session, query_str=query_str, order_by=order_by
        )
        return result
    except Exception as e:
        logger.exception(f"Failed to fetch orders: {str(e)}")
        raise DetailedHTTPException()


@router.get("/{order_id}", response_model=OrderOutSchema)
async def read_order(db_session: DBSession, order_id: UUID4):
    try:
        result = await order_crud.get(db_session=db_session, id=order_id)
        if result is None:
            raise OrderNotFound()
        return result
    except OrderNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to fetch order {order_id}: {str(e)}")
        raise DetailedHTTPException()


@router.post("/", response_model=OrderCreateSchema)
async def add_order(db_session: DBSession, order: OrderCreateSchema):
    try:
        result = await order_crud.create(db_session=db_session, order=order)
        return result
    except Exception as e:
        logger.exception(f"Failed to create order: {str(e)}")
        raise DetailedHTTPException()


@router.put("/{order_id}", response_model=OrderOutMinimalSchema)
async def edit_order(db_session: DBSession, order: OrderUpdateSchema, order_id: UUID4):
    try:
        db_order = await order_crud.get(db_session=db_session, id=order_id)
        if db_order is None:
            raise OrderNotFound()
        result = await order_crud.update(
            db_session=db_session, db_order=db_order, order=order
        )
        return result
    except OrderNotFound:
        raise
    except Exception as e:
        logger.exception(f"Failed to update order {order_id}: {str(e)}")
        raise DetailedHTTPException()
