from pydantic import UUID4, BaseModel


class BaseOrderSchema(BaseModel):
    number: str | None = None


class OrderCreateSchema(BaseOrderSchema):
    pass


class OrderUpdateSchema(OrderCreateSchema):
    id: UUID4


class OrderOutMinimalSchema(OrderUpdateSchema):
    pass


class OrderOutSchema(OrderOutMinimalSchema):
    pass
