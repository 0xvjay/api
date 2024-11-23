from api.exceptions import NotFound


class UserNotFound(NotFound):
    detail = "User Not Found"
