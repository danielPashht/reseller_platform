from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class OrderModel(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    order_items = relationship("OrderItemModel", back_populates="order")


class ItemModel(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    price = Column(Float, nullable=False)
    order_items = relationship("OrderItemModel", back_populates="item")


class OrderItemModel(Base):
    __tablename__ = 'order_item'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('order.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    order = relationship("OrderModel", back_populates="order_items")
    item = relationship("ItemModel", back_populates="order_items")
