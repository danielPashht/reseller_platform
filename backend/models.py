from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ItemModel(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(String(255), nullable=True)
    image = Column(String(255), nullable=True)
    price = Column(Float, nullable=False)

    order_items = relationship("OrderItemModel", back_populates="item")


class OrderModel(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    user_telegram_id = Column(Integer, nullable=False)
    total = Column(Float, nullable=False)
    status = Column(String, default="created", nullable=False)

    order_items = relationship("OrderItemModel", back_populates="order")


class OrderItemModel(Base):
    __tablename__ = 'order_item'
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('order.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    quantity = Column(Integer, default=1)

    order = relationship("OrderModel", back_populates="order_items")
    item = relationship("ItemModel", back_populates="order_items")
