from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import Query

from database import SessionLocal
from models import Event, EventRubric, Rubric, Favorite, User, Ticket
from utils.security import get_current_user


router = APIRouter(prefix="/api/events", tags=["events"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_events(
    rubric: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Event).filter(Event.archived == False)
    if rubric:
        query = query.join(EventRubric).join(Rubric).filter(Rubric.code == rubric)

    total = query.count()
    events = query.offset((page - 1) * per_page).limit(per_page).all()

    favs = {f.event_id for f in db.query(Favorite).filter(Favorite.user_id == current_user.id).all()}
    tickets = {t.event_id for t in db.query(Ticket).filter(Ticket.user_id == current_user.id).all()}

    results = []
    for e in events:
        results.append({
            "id": e.id,
            "title": e.title,
            "image_url": e.image_url,
            "is_favorite": e.id in favs,
            "is_ticket": e.id in tickets
        })

    return {
        "page": page,
        "per_page": per_page,
        "total": total,
        "events": results
    }
