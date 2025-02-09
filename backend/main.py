from contextlib import asynccontextmanager
from sqlalchemy import text
from fastapi import FastAPI, Depends
from sqladmin import Admin

from admin_views import ItemAdmin, OrderAdmin
from models import Base, Item

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        print("Creating tables...")
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
        print("Tables created successfully!")
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
admin = Admin(app, engine, session_maker=SessionLocal)
admin.add_view(ItemAdmin)
admin.add_view(OrderAdmin)


@app.get("/items/")
async def get_items(session: AsyncSession = Depends(get_session)):
    result = await session.execute(text("SELECT * FROM item"))
    items = result.scalars().all()
    return items

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8008, reload=True)
