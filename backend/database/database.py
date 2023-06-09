import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from backend.settings import settings


def database_url(async_connection: bool = True) -> URL:
    return sqlalchemy.engine.URL.create(
        drivername="postgresql+asyncpg" if async_connection else "postgresql",
        username=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        database=settings.db_name,
        port=settings.db_port,
    )


# poolclass=NullPool was needed here since otherwise we had connection errors.
# Maybe there is a more performant solution.
engine = create_async_engine(database_url(), echo=False, poolclass=NullPool)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncSession:
    async with engine.begin() as conn:
        async with async_session(bind=conn) as session:
            yield session


Base = declarative_base()
