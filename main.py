import asyncio
import json
import logging
import random
import threading
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, List

from fastapi import FastAPI
from fastapi import Header, Depends, Response
from fastapi.exceptions import HTTPException
from sqladmin import Admin
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from models import Base, OrderItemModel, OrderModel, ItemModel
import config
from schemas import ItemSchema


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("reseller")

engine = create_async_engine(config.get_db_url(), echo=True)
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def create_tables():
    """
    Creates database tables.
    This function is run before starting to serve requests.
    """
    async with engine.begin() as conn:
        try:
            _logger = logging.getLogger("sqlalchemy.engine")
            _logger.setLevel(logging.DEBUG)
            await conn.run_sync(Base.metadata.create_all, checkfirst=True)
            logger.info("DB tables created")
        except SQLAlchemyError as e:
            logger.error(f"Error creating tables: {e}")
            raise


async def seed_data():
    """
    Seeds the database with initial data.
    This function is run after table creation.
    """
    items = generate_items()
    async with SessionLocal() as session:
        for item in items:
            new_item = ItemModel(**item)
            await session.merge(new_item)
        await session.commit()
    logger.info("DB seeded")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting an async session.
    """
    async with SessionLocal() as session:
        yield session


def generate_items(num_items=10):
    items = []
    for i in range(num_items):
        item = {
            "name": f"Item {i+1}",
            "description": f"Description for item {i+1}",
            "price": round(random.uniform(10.0, 100.0), 2)
        }
        items.append(item)
    return items


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the startup and shutdown of the application.
    """
    await create_tables()
    await seed_data()

    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
admin = Admin(app, engine, session_maker=SessionLocal)


# Middleware
async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != config.TG_SECRET:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key


# def callback(ch, method, properties, body):
#     """ Process consumed order message """
#     message = json.loads(body)
#     order_data = message.get('order_data')
#     order_items = message.get('order_items')
#
#     async def process_order():
#         async with SessionLocal() as session:
#             new_order = OrderModel(**order_data)
#             session.add(new_order)
#             await session.flush()
#
#             for item in order_items:
#                 order_item = OrderItemModel(
#                     order_id=new_order.id,
#                     item_id=item['item_id'],
#                     quantity=item['quantity']
#                 )
#                 session.add(order_item)
#
#             await session.commit()
#             await session.refresh(new_order)
#         # TODO: notify admin
#         # TODO: send update for order status in Telegram

#    asyncio.create_task(process_order())


# def start_rabbit_consumer():
#     config.rabbit_channel.basic_consume(queue="order_queue", on_message_callback=callback, auto_ack=True)
#     config.rabbit_channel.start_consuming()
#
#
# @app.on_event("startup")
# def startup_event():
#     consumer_thread = threading.Thread(target=start_rabbit_consumer)
#     consumer_thread.start()


@app.get("/items/", dependencies=[Depends(verify_api_key)])
async def get_items(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(ItemModel))
    items = result.fetchall()
    return [ItemSchema.model_validate(item[0]) for item in items]


@app.post("/order/", dependencies=[Depends(verify_api_key)])
async def create_order(order_data: Dict, session: AsyncSession = Depends(get_session)):
    # todo: use order schema not dict
    order_items_data: list = order_data.pop("order_items", [])
    if not order_items_data:
        raise HTTPException(status_code=400, detail="Order items are required")

    try:
        async with session.begin():
            new_order = OrderModel(**order_data)
            session.add(new_order)
            await session.flush()

            for item_data in order_items_data:
                order_item = OrderItemModel(order_id=new_order.id, **item_data)
                session.add(order_item)

            await session.flush()
        await session.refresh(new_order)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error saving order data to DB: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating order: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error creating order: {str(e)}")
    logger.info(f"Order created: {new_order}")
    return Response(status_code=201)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True, log_level="debug")
