from datetime import datetime
from typing import List

from pydantic import UUID4, BaseModel

from .constant import TicketStatus


class BaseTicketSchema(BaseModel):
    subject: str


class TicketCreateSchema(BaseTicketSchema):
    description: str | None = None


class TicketUpdateSchema(BaseTicketSchema):
    id: UUID4
    status: TicketStatus


class TicketOutMinimalSchema(TicketUpdateSchema):
    pass


class TicketOutSchema(TicketOutMinimalSchema):
    messages: List["MessageOutSchema"] = []

    created_at: datetime
    updated_at: datetime | None


class BaseMessageSchema(BaseModel):
    content: str
    user_id: UUID4
    ticket_id: UUID4


class MessageCreateSchema(BaseMessageSchema):
    pass


class MessageUpdateSchema(MessageCreateSchema):
    id: UUID4


class MessageOutSchema(MessageUpdateSchema):
    created_at: datetime
    updated_at: datetime | None
