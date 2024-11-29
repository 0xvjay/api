from api.models import BaseTimeStamp
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from api.order.models import Order  # noqa: F401


class User(BaseTimeStamp):
    __tablename__ = "user_user"

    username = Column(String(100), unique=True, index=True)
    email = Column(String(100), nullable=False, unique=True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    password = Column(String(128), nullable=False)
    last_login = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)

    is_superuser = Column(Boolean, default=False)

    groups = relationship(
        "Group", secondary="auth_user_group", back_populates="users", lazy="joined"
    )
    orders = relationship("Order", back_populates="user")
    addresses = relationship("UserAddress", backref="user")
