from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from app.core.config import env
from app.core.logging import get_logger


logger = get_logger("app.db.postgres")


class PostgresDB:
    engine: AsyncEngine | None = None
    session_factory: async_sessionmaker[AsyncSession] | None = None


postgres = PostgresDB()


async def connect_to_postgres() -> None:
    postgres.engine = create_async_engine(
        env.postgres_url,
        echo=True,
        future=True,
    )

    # try:
    #     async with postgres.engine.connect() as conn:
    #         await conn.execute(text("SELECT 1"))
    # except Exception as e:
    #     logger.error(f"Postgres Connection error: {e}")
    #     raise e

    postgres.session_factory = async_sessionmaker(
        postgres.engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    logger.info("PostgreSQL Connected Successfully.")


async def close_postgres_connection() -> None:
    """
    Cleanly dispose of the async engine during shutdown.
    """
    if postgres.engine:
        await postgres.engine.dispose()

    logger.info("PostgreSQL Connection Closed successfully.")


async def get_postgres_session() -> AsyncSession:
    """
    Dependency injection helper for routes & services.
    Example use:
        async with get_session() as session:
            ...
    """
    if not postgres.session_factory:
        raise RuntimeError("PostgreSQL is not initialized")

    return postgres.session_factory()
