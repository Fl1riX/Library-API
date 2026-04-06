import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from src.infrastructure.db.database import Base


@pytest_asyncio.fixture(scope="function")
async def db_session():
    db_url = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(db_url)
    
    SessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        async with SessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()
    
    await engine.dispose()