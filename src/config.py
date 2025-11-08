from pydantic_settings import SettingsConfigDict, BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DATABASE_URL_asyncpg(self):
        # URL для асинхронного подключения через asyncpg
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


    # Загрузка переменных из .env, который лежит на уровень выше текущего файла
    model_config = SettingsConfigDict(env_file=Path(__file__).resolve().parent / ".env")

# Инициализация настроек при старте приложения
settings = Settings()