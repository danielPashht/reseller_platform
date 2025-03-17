from typing import Dict
from pydantic import BaseModel


class Order(BaseModel):
    user_id: int
    username: str
    items: list[Dict]
    total_price: float


class Item(BaseModel):
    id: int
    name: str
    price: str
    description: str | None


class ItemDeleteMessage(BaseModel):
    channel: str
    id: int


class ItemUpdateMessage(BaseModel):
    id: int
    name: str
    price: float | int
    description: str | None
