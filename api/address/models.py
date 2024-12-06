from sqlalchemy import UUID, Boolean, Column, ForeignKey, Integer, String, Text

from api.models import BaseTimeStamp, BaseUUID


class BaseAddress(BaseUUID):
    """
    Superclass address object

    This is subclassed and extended to provide models for
    user, shipping and billing addresses.
    """

    __abstract__ = True

    first_name = Column(String(255))
    last_name = Column(String(255))

    line1 = Column(String(255))
    line2 = Column(String(255))
    line3 = Column(String(255))
    state = Column(String(255))
    postcode = Column(String(64))
    country = Column(String(255), nullable=False)


class ShippingAddress(BaseAddress):
    """
    A shipping address.

    A shipping address should not be edited once the order has been placed -
    it should be read-only after that.

    """

    __tablename__ = "address_shipping_address"

    phone_number = Column(String(20))
    notes = Column(Text)


class BillingAddress(BaseAddress):
    __tablename__ = "address_billing_address"

    pass


class UserAddress(BaseAddress, BaseTimeStamp):
    """
    A user's address.  A user can have many of these and together they form an
    'address book' of sorts for the user.

    We use a separate model for shipping and billing (even though there will be
    some data duplication) because we don't want shipping/billing addresses
    changed or deleted once an order has been placed.  By having a separate
    model, we allow users the ability to add/edit/delete from their address
    book without affecting orders already placed.
    """

    __tablename__ = "address_user_address"

    phone_number = Column(String(20))
    notes = Column(Text)
    user_id = Column(UUID, ForeignKey("user_user.id", ondelete="CASCADE"))

    #: Whether this address is the default for shipping
    is_default_for_shipping = Column(Boolean, default=False)
    #: Whether this address should be the default for billing.
    is_default_for_billing = Column(Boolean, default=False)

    #: We keep track of the number of times an address has been used
    #: as a shipping address so we can show the most popular ones
    #: first at the checkout.
    num_orders_as_shipping_address = Column(Integer, default=0)

    #: Same as previous, but for billing address.
    num_orders_as_billing_address = Column(Integer, default=0)
