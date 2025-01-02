from datetime import datetime

from pydantic import UUID4, BaseModel

from .constant import USAGE_CHOICES


class BaseVoucherSchema(BaseModel):
    name: str
    code: str
    usage: USAGE_CHOICES

    start_datetime: datetime
    end_datetime: datetime


class VoucherCreateSchema(BaseVoucherSchema):
    pass


class VoucherUpdateSchema(VoucherCreateSchema):
    id: UUID4


class VoucherOutMinimalSchema(VoucherUpdateSchema):
    pass


class VoucherOutSchema(VoucherOutMinimalSchema):
    created_at: datetime
    updated_at: datetime | None
