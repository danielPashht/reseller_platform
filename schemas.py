from typing import List

from pydantic import BaseModel


class ItemSchema(BaseModel):
    id: int | None = None
    name: str
    description: str | None = None
    price: float

    class Config:
        from_attributes = True


class OrderItemSchema(BaseModel):
    id: int | None = None
    order_id: int
    item_id: int

    class Config:
        from_attributes = True


class OrderSchema(BaseModel):
    id: int | None = None
    user_id: int
    total_price: float
    order_items: List[OrderItemSchema]

    class Config:
        from_attributes = True
