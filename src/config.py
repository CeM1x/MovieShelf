from pydantic_settings import SettingsConfigDict, BaseSettings
from pathlib import Path
from dotenv import load_dotenv
import os


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str = "H256"

    @property
    def DATABASE_URL_asyncpg(self):
        # URL для асинхронного подключения через asyncpg
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


    # Загрузка переменных из .env, который лежит на уровень выше текущего файла
    model_config = SettingsConfigDict(env_file=Path(__file__).resolve().parent / ".env")


# Инициализация настроек при старте приложения
settings = Settings()