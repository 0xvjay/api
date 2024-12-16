from enum import StrEnum


class PermissionAction(StrEnum):
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class PermissionObject(StrEnum):
    GROUP = "group"
    USER = "user"
    USER_ADDRESS = "user_address"
    ORDER = "order"
    CATEGORY = "category"
    SUB_CATEGORY = "sub_category"
    PRODUCT = "product"
    ADMIN_LOG = "admin_log"
    SITE_SETTING = "site_setting"
    EXPORT = "export"
    COMPANY = "company"
    PROJECT = "project"
    TICKET = "ticket"
