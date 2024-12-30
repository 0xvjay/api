import logging
from pathlib import Path
from typing import Any, Dict, List

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from api.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        """Initialize email service with configuration."""
        self.conf = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            TEMPLATE_FOLDER=Path(__file__).parent / "templates/email/",
        )
        self.fastmail = FastMail(self.conf)

    async def send_email(
        self,
        recipients: List[EmailStr],
        subject: str,
        template_name: str,
        data: Dict[str, Any] = None,
    ):
        """Send templated email to recipients."""
        try:
            message = MessageSchema(
                subject=subject,
                recipients=recipients,
                template_body=data or {},
                subtype=MessageType.html,
            )

            await self.fastmail.send_message(message, template_name=template_name)
            logger.info(f"Email sent successfully to {recipients}")

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            raise

    async def send_order_confirmation(
        self, email: EmailStr, order_data: Dict[str, Any]
    ):
        """Send order confirmation email."""
        await self.send_email(
            recipients=[email],
            subject="Order Confirmation",
            template_name="order_confirmation.html",
            data=order_data,
        )

    async def send_password_reset(self, email: EmailStr, reset_token: str):
        """Send password reset email."""
        await self.send_email(
            recipients=[email],
            subject="Password Reset Request",
            template_name="password_reset.html",
            data={"reset_token": reset_token},
        )

    async def send_ticket_update(self, email: EmailStr, ticket_data: Dict[str, Any]):
        """Send ticket update notification."""
        await self.send_email(
            recipients=[email],
            subject=f"Ticket Update - {ticket_data['subject']}",
            template_name="ticket_update.html",
            data=ticket_data,
        )


email_service = EmailService()
