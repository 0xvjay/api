from api.exceptions import NotFound, BadRequest


class VoucherNotFound(NotFound):
    detail = "Voucher not found"


class VoucherNameOrCodeExists(BadRequest):
    detail = "Voucher name or code exists"
