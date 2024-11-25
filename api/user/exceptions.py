from api.exceptions import NotFound, BadRequest


class UserNotFound(NotFound):
    detail = "User Not Found"


class UserEmailOrNameExists(BadRequest):
    detail = "User with email or username already exists"
