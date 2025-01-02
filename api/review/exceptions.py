from api.exceptions import NotFound


class ReviewNotFound(NotFound):
    detail = "Product Review not found"
