from api.exceptions import NotFound, BadRequest


class OrderNotFound(NotFound):
    detail = "Order not found"
