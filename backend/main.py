from contextlib import asynccontextmanager
from sqlalchemy import text
from fastapi import FastAPI, Depends
from sqladmin import Admin

from admin_views import ItemAdmin, OrderAdmin
from models import Base, OrderModel, OrderItemModel
from schemas import OrderItemSchema, OrderSchema

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# --- Database --- #
DATABASE_URL = "postgresql+asyncpg://postgres:946815@localhost:5432/tg_shop"
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_session():
    async with SessionLocal() as session:
        yield session


# --- FastAPI app --- #
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

# --- Admin --- #
admin = Admin(app, engine, session_maker=SessionLocal)
admin.add_view(ItemAdmin)
admin.add_view(OrderAdmin)


# --- Views --- #
@app.post("/orders/")
async def create_order(
        order_data: OrderSchema,
        session: AsyncSession = Depends(get_session)
):
    order_data_dict = order_data.model_dump()
    order_data_dict.pop('order_items', None)

    new_order = OrderModel(**order_data_dict)

    session.add(new_order)
    await session.flush()

    for item in order_data.order_items:
        order_item = OrderItemModel(order_id=new_order.id, item_id=item.item_id, quantity=item.quantity)
        session.add(order_item)

    await session.commit()
    await session.refresh(new_order)

    return new_order

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8008, reload=True)
