from api.exceptions import BadRequest, NotFound


class OrderNotFound(NotFound):
    detail = "Order not found"


class InsufficientCredit(BadRequest):
    detail = "Insufficient credit available for purchase"
