from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base
from config import settings


engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# create table on start (only dev variant!)
def init_db():
    Base.metadata.create_all(bind=engine)
