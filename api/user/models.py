from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from api.auth.models import CompanyGroup, UserGroup  # noqa: F401
from api.catalogue.models import Product  # noqa: F401
from api.models import BaseTimeStamp, BaseUUID
from api.ticket.models import TicketUser  # noqa: F401


class AbstractUser(BaseTimeStamp):
    __abstract__ = True

    email = Column(String(100), nullable=False, unique=True, index=True)
    password = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True)


class User(AbstractUser):
    __tablename__ = "user_user"

    username = Column(String(100), unique=True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    last_login = Column(DateTime(timezone=True))
    is_superuser = Column(Boolean, default=False)

    company_id = Column(UUID, ForeignKey("user_company.id", ondelete="CASCADE"))
    company = relationship("Company", back_populates="users")
    groups = relationship("Group", secondary="auth_user_group", back_populates="users")
    tickets = relationship(
        "Ticket", secondary="ticket_ticket_user", back_populates="users"
    )


class Company(AbstractUser):
    __tablename__ = "user_company"

    billing_code = Column(String(255), unique=True, nullable=False)

    users = relationship("User", back_populates="company")
    groups = relationship(
        "Group", secondary="auth_company_group", back_populates="companies"
    )


class ProjectProduct(BaseUUID):
    __tablename__ = "user_project_product"

    project_id = Column(UUID, ForeignKey("user_project.id", ondelete="CASCADE"))
    product_id = Column(UUID, ForeignKey("catalogue_product.id", ondelete="CASCADE"))


class Project(BaseTimeStamp):
    __tablename__ = "user_project"

    name = Column(String(255), index=True)
    code = Column(String(255))
    description = Column(Text)
    priority = Column(Integer, default=0)
    start_date = Column(Date)
    end_date = Column(Date)
    company_id = Column(UUID, ForeignKey("user_company.id", ondelete="CASCADE"))

    company = relationship("Company", backref="projects")
    products = relationship(
        "Product", secondary="user_project_product", backref="projects"
    )
    product_limits = relationship("ProductLimit", back_populates="project")


class TaxLimit(BaseTimeStamp):
    __tablename__ = "user_tax_limit"

    project_id = Column(UUID, ForeignKey("user_project.id", ondelete="RESTRICT"))
    user_id = Column(UUID, ForeignKey("user_user.id", ondelete="SET NULL"))
    amount = Column(Numeric(12, 2))
    year = Column(Integer, default=0)


class Credit(BaseTimeStamp):
    __tablename__ = "user_credit"

    user_id = Column(UUID, ForeignKey("user_user.id", ondelete="CASCADE"))
    project_id = Column(UUID, ForeignKey("user_project.id", ondelete="RESTRICT"))
    amount = Column(Numeric(12, 2))


class Transaction(BaseTimeStamp):
    __tablename__ = "user_transaction"

    credit_id = Column(UUID, ForeignKey("user_credit.id", ondelete="CASCADE"))
    order_id = Column(UUID, ForeignKey("order_order.id", ondelete="CASCADE"))
    amount = Column(Numeric(12, 2))
    is_tax = Column(Boolean, default=False)


class ProductLimit(BaseUUID):
    __tablename__ = "user_product_limit"

    project_id = Column(UUID, ForeignKey("user_project.id", ondelete="CASCADE"))
    product_id = Column(UUID, ForeignKey("catalogue_product.id", ondelete="CASCADE"))

    amount = Column(Numeric(12, 2))
    absolute_limit = Column(Boolean, default=False)

    project = relationship("Project", back_populates="product_limits")
    product = relationship("Product", backref="product_limits")
