from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    select,
    func,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class OrderModel(Base):
    __tablename__ = "order"
    created_at = Column(DateTime, default=datetime.utcnow)
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    username = Column(String(255), nullable=True)
    total_price = Column(Float, nullable=False)
    order_items = relationship(
        "OrderItemModel",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    @hybrid_property
    def item_names(self):
        if not self.order_items:
            return "No items"
        return ", ".join([item.item.name for item in self.order_items if item.item])

    @item_names.expression
    def item_names(cls):
        return (
            select(func.group_concat(ItemModel.name, ", "))
            .select_from(OrderItemModel)
            .join(ItemModel, OrderItemModel.item_id == ItemModel.id)
            .where(OrderItemModel.order_id == cls.id)
            .label("item_names")
        )


class ItemModel(Base):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    price = Column(Float, nullable=False)
    order_items = relationship("OrderItemModel", back_populates="item")


class OrderItemModel(Base):
    __tablename__ = "order_item"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(
        Integer, ForeignKey("order.id", ondelete="CASCADE"), nullable=False
    )
    item_id = Column(Integer, ForeignKey("item.id"), nullable=False)
    order = relationship("OrderModel", back_populates="order_items")
    item = relationship("ItemModel")
