from typing import List

from pydantic import BaseModel


class ItemSchema(BaseModel):
    id: int | None = None
    name: str
    description: str
    image: str
    price: float


class OrderItemSchema(BaseModel):
    id: int | None = None
    item_id: int
    quantity: int


class OrderSchema(BaseModel):
    id: int | None = None
    username: str
    user_telegram_id: int
    order_items: List[OrderItemSchema]
    total: float
    status: str = "created"
