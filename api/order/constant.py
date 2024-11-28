from enum import StrEnum


class OrderStatus(StrEnum):
    INIT = "INIT"  # Initial state when order is created
    PENDING = "PENDING"  # Order is being processed
    CONFIRMED = "CONFIRMED"  # Order has been confirmed
    PAID = "PAID"  # Payment has been received
    PROCESSING = "PROCESSING"  # Order is being prepared/processed
    SHIPPED = "SHIPPED"  # Order has been shipped
    DELIVERED = "DELIVERED"  # Order has been delivered
    CANCELLED = "CANCELLED"  # Order has been cancelled
    REFUNDED = "REFUNDED"  # Order has been refunded
    RETURNED = "RETURNED"  # Order has been returned
