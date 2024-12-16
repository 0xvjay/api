from api.exceptions import NotFound


class TicketNotFound(NotFound):
    detail = "Ticket not found"
