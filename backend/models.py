from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(String(255), nullable=True)
    image = Column(String(255), nullable=True)
    price = Column(Float, nullable=False)

    order_items = relationship("OrderItem", back_populates="item")


class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    user_telegram_id = Column(Integer, nullable=False)
    total = Column(Float, nullable=False)
    status = Column(String, default="created", nullable=False)

    order_items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = 'order_item'
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('order.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    quantity = Column(Integer, default=1)

    # Relationships
    order = relationship("Order", back_populates="order_items")
    item = relationship("Item", back_populates="order_items")
