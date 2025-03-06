import asyncio
import json
import logging
import threading
from contextlib import asynccontextmanager
import random

from sqlalchemy import text
from fastapi import FastAPI, Depends, Header, HTTPException
from sqladmin import Admin

from models import Base, OrderModel, OrderItemModel, ItemModel
import config
from schemas import ItemSchema, OrderSchema
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


engine = create_async_engine(config.get_db_url(), echo=True)
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("reseller")


def load_items_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


async def get_session():
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
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
        logger.info("DB tables created")
        # if not (await conn.execute(text("SELECT 1 FROM item")).fetchone()):
        #     items = generate_items()
        #     async with SessionLocal() as session:
        #         for item in items:
        #             new_item = ItemModel(**item)
        #             session.add(new_item)
        #         await session.commit()
        #         logger.info("Initial items loaded to DB")

    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
admin = Admin(app, engine, session_maker=SessionLocal)


# Middleware
async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != config.TG_SECRET:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key


def callback(ch, method, properties, body):
    """ Process consumed order message """
    message = json.loads(body)
    order_data = message.get('order_data')
    order_items = message.get('order_items')

    async def process_order():
        async with SessionLocal() as session:
            new_order = OrderModel(**order_data)
            session.add(new_order)
            await session.flush()

            for item in order_items:
                order_item = OrderItemModel(
                    order_id=new_order.id,
                    item_id=item['item_id'],
                    quantity=item['quantity']
                )
                session.add(order_item)

            await session.commit()
            await session.refresh(new_order)
        # TODO: notify admin
        # TODO: send update for order status in Telegram

    asyncio.create_task(process_order())


def start_rabbit_consumer():
    config.rabbit_channel.basic_consume(queue="order_queue", on_message_callback=callback, auto_ack=True)
    config.rabbit_channel.start_consuming()


@app.on_event("startup")
def startup_event():
    consumer_thread = threading.Thread(target=start_rabbit_consumer)
    consumer_thread.start()


@app.get("/items/", dependencies=[Depends(verify_api_key)])
async def get_items(session: AsyncSession = Depends(get_session)):
    query = text("SELECT * FROM item")
    result = await session.execute(query)
    items = result.fetchall()
    return [ItemSchema.from_orm(item) for item in items]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True, log_level="debug")
