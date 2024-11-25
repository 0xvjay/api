from api.exceptions import BadRequest, NotFound


class InactiveUser(BadRequest):
    detail = "Inactive User"


class GroupNotFound(NotFound):
    detail = "Group not found"


class GroupExists(BadRequest):
    detail = "Group name already exists"
