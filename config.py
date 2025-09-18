import os

from pydantic_settings import BaseSettings


BASE_DIR = "/opt/afisha-server"


class Settings(BaseSettings):
    # paths
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "uploads/avatars")

    # db
    DATABASE_URL: str =f"sqlite:///{os.path.join(BASE_DIR, 'db/afisha.sqlite3')}"

    # JWT
    JWT_SECRET_KEY: str = "secret_key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    class Config:
        env_file = ".env"


settings = Settings()
