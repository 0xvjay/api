from enum import StrEnum


class TicketStatus(StrEnum):
    INIT = "INIT"
    IN_PROGRESS = "IN PROGRESS"
    ON_HOLD = "ON_HOLD"
    COMPLETED = "COMPLETED"
    REOPENED = "REOPENED"
    CANCELED = "CANCELED"
