from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    ENV: str
    DATABASE_URL: str
    REDIS_HOST: str
    REDIS_PORT: int

    REDIS_USERNAME: str | None = None
    REDIS_PASSWORD: str | None = None
    REDIS_SSL: bool = False 

    class Config:
        env_file = ".env.local"


env = os.getenv("ENV", "local")

if env == "prod":
    settings = Settings()
else:
    settings = Settings(_env_file=".env.local")