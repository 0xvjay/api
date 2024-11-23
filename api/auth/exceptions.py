from api.exceptions import NotFound, BadRequest


class InactiveUser(BadRequest):
    detail = "Inactive User"


class GroupNotFound(NotFound):
    detail = "Group not found"
