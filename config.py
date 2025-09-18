from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # paths
    DATA_DIR: str = "data/"
    UPLOAD_DIR: str = "uploads/avatars/"

    # db
    DATABASE_URL: str ="sqlite:///.db/afisha.sqlite3"

    # JWT
    JWT_SECRET_KEY: str = "secret_key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    class Config:
        env_file = ".env"


settings = Settings()
