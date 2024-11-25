from enum import StrEnum


class PermissionAction(StrEnum):
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class PermissionObject(StrEnum):
    GROUP = "group"
    USER = "user"
