import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi_utils.tasks import repeat_every

from config import settings
from database import init_db, SessionLocal
from utils.logging_utils import setup_logging
from services.events_loader import get_latest_data_file, load_events_from_json

from routers import auth, events, favorites, tickets


setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        latest_file = get_latest_data_file(settings.DATA_DIR)
        if latest_file:
            logger.info(f"[{datetime.now()}] Initial DB update from {latest_file}")
            load_events_from_json(db, latest_file)
        else:
            logger.warning(f"[{datetime.now()}] No data files found in {settings.DATA_DIR}")
    finally:
        db.close()

    @repeat_every(seconds=60*60*24)
    def update_db_from_file_task():
        db = SessionLocal()
        try:
            latest_file = get_latest_data_file(settings.DATA_DIR)
            if latest_file:
                logger.info(f"[{datetime.now()}] Updating DB from {latest_file}")
                load_events_from_json(db, latest_file)
        finally:
            db.close()

    yield
    logger.info(f"[{datetime.now()}] Server shutting down…")


app = FastAPI(title="Afisha API", lifespan=lifespan)
# Routers
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(favorites.router)
app.include_router(tickets.router)
