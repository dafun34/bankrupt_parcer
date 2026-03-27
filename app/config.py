import os
from pathlib import Path
from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=find_dotenv(), extra="ignore")
    # postgres
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: str = Field(default="5432")
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_DB: str = Field(default="postgres")
    # logging
    LOGGING_LEVEL: str = Field(description="Logging level", default="DEBUG")
    # input file
    INPUT_FILE_PATH: str = Field(
        description="Path to the input Excel file with INNs, depends base dir path")

    @property
    def postgres_connection_string(self) -> str:
        """Формирование строки подключения к PostgreSQL."""
        return "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
            self.POSTGRES_USER,
            self.POSTGRES_PASSWORD,
            self.POSTGRES_HOST,
            self.POSTGRES_PORT,
            self.POSTGRES_DB,
        )
    @property
    def base_dir_path(self) -> Path:
        current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        return current_dir.parent

settings = Settings()
