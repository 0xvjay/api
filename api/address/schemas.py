from pydantic import BaseModel


class BaseAddressSchema(BaseModel):
    first_name: str | None = None
    last_name: str | None = None

    line1: str | None = None
    line2: str | None = None
    line3: str | None = None
    state: str | None = None
    postcode: str | None = None
    country: str
