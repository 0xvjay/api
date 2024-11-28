from sqlalchemy import (
    UUID,
    Column,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship

from api.models import BaseTimeStamp, BaseUUID

from .constant import OrderStatus


class Order(BaseTimeStamp):
    __tablename__ = "order_order"

    number = Column(String(128), index=True, unique=True)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("user_user.id", ondelete="SET NULL")
    )
    total_incl_tax = Column(Numeric(12, 2))
    total_excl_tax = Column(Numeric(12, 2))

    shipping_incl_tax = Column(Numeric(12, 2), default=0)
    shipping_excl_tax = Column(Numeric(12, 2), default=0)

    status = Column(Enum(OrderStatus))
    guest_email = Column(String(255))

    lines = relationship("Line", backref="order")


class Line(BaseUUID):
    __tablename__ = "order_line"

    order_id = Column(
        UUID(as_uuid=True), ForeignKey("order_order.id", ondelete="CASCADE")
    )
    product_id = Column(
        UUID(as_uuid=True), ForeignKey("catalogue_product.id", ondelete="SET NULL")
    )
    quantity = Column(Integer, default=1)

    line_price_incl_tax = Column(Numeric(12, 2))
    line_price_excl_tax = Column(Numeric(12, 2))

    line_price_before_discounts_incl_tax = Column(Numeric(12, 2))
    line_price_before_discounts_excl_tax = Column(Numeric(12, 2))

    unit_price_incl_tax = Column(Numeric(12, 2))
    unit_price_excl_tax = Column(Numeric(12, 2))
