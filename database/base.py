from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from database.models.models import Base
import config

# Создаем асинхронный движок для PostgreSQL
engine = create_async_engine(
    config.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=True
)

# Современный способ создания асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False
)

async def get_db():
    """Генератор сессий БД"""
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    """Создает таблицы в БД"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Таблицы в базе данных созданы")