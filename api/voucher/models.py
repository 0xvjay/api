from decimal import Decimal

from sqlalchemy import (
    UUID,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from api.models import BaseTimeStamp, BaseUUID

from .constant import USAGE_CHOICES


class Voucher(BaseTimeStamp):
    __tablename__ = "voucher_voucher"
    name = Column(String(128), nullable=False, unique=True)
    code = Column(String(128), nullable=False, unique=True, index=True)
    usage = Column(Enum(USAGE_CHOICES))

    start_datetime = Column(DateTime, index=True)
    end_datetime = Column(DateTime, index=True)

    discount = Column(Numeric(12, 2), default=Decimal(0))
    num_orders = Column(Integer, default=0)

    def __init__(self, *args, **kwargs):
        if "code" in kwargs:
            kwargs["code"] = kwargs["code"].upper()
        super().__init__(*args, **kwargs)

    applications = relationship("VoucherApplication", back_populates="voucher")


class VoucherApplication(BaseUUID):
    __tablename__ = "voucher_voucher_application"

    voucher_id = Column(UUID, ForeignKey("voucher_voucher.id", ondelete="CASCADE"))
    user_id = Column(UUID, ForeignKey("user_user.id", ondelete="CASCADE"))
    order_id = Column(UUID, ForeignKey("order_order.id", ondelete="CASCADE"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    voucher = relationship("Voucher", back_populates="applications")
