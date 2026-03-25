from pathlib import Path

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from alembic.config import Config as AlembicConfig
from alembic import command
from app.config import settings
from app.logging_config import logger

engine = create_async_engine(
    settings.postgres_connection_string,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


def run_migrations() -> None:
    """Запустить миграции alembic."""
    postgres_url = settings.postgres_connection_string.replace("postgresql+asyncpg", "postgresql")
    base_dir = Path(__file__).parent.parent.parent
    alembic_ini_path = base_dir / "alembic.ini"
    alembic_location_path = base_dir / "alembic"
    alembic_config = AlembicConfig(alembic_ini_path)
    alembic_config.set_main_option("script_location", str(alembic_location_path))
    alembic_config.set_main_option("sqlalchemy.url", postgres_url)

    # Migrations
    logger.debug("start alembic upgrade head")
    try:
        command.upgrade(alembic_config, "head")
    except Exception as exc:
        logger.error(f"failed alembic upgrade head: {repr(exc)}")
        raise
    logger.debug("finish alembic upgrade head")
