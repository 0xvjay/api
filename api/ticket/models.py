from sqlalchemy import UUID, Column, Enum, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from api.models import BaseTimeStamp, BaseUUID

from .constant import TicketStatus


class TicketUser(BaseUUID):
    __tablename__ = "ticket_ticket_user"

    ticket_id = Column(UUID, ForeignKey("ticket_ticket.id", ondelete="CASCADE"))
    user_id = Column(UUID, ForeignKey("user_user.id", ondelete="CASCADE"))


class Ticket(BaseTimeStamp):
    __tablename__ = "ticket_ticket"

    subject = Column(String(255))
    description = Column(Text)
    status = Column(Enum(TicketStatus), nullable=False, default=TicketStatus.INIT)

    users = relationship(
        "User", secondary="ticket_ticket_user", back_populates="tickets"
    )
    messages = relationship("Message", backref="ticket")


class Message(BaseTimeStamp):
    __tablename__ = "ticket_message"

    content = Column(Text)
    ticket_id = Column(UUID, ForeignKey("ticket_ticket.id", ondelete="CASCADE"))
    user_id = Column(UUID, ForeignKey("user_user.id", ondelete="CASCADE"))
