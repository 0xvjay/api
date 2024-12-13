from api.exceptions import BadRequest, NotFound


class UserNotFound(NotFound):
    detail = "User Not Found"


class UserEmailOrNameExists(BadRequest):
    detail = "User with email or username already exists"


class UserAddressNotFound(NotFound):
    detail = "User address not found"


class CompanyNotFound(NotFound):
    detail = "Company not found"


class ProjectNotFound(NotFound):
    detail = "Project not found"
