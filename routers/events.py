from typing import Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from fastapi import Query

from database import SessionLocal
from models import Event, EventRubric, Rubric, Favorite, Ticket
from utils.security import get_optional_user


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
    start: int = Query(1, ge=1),
    pages: int = Query(1, ge=1, le=10),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    page_size = 12
    offset = (start - 1) * page_size
    limit = pages * page_size

    # init user_id, if token sended
    user_id = None
    if authorization:
        try:
            user = get_optional_user(authorization, db)
            if user:
                user_id = user.id
        except:
            pass  # token invalid — the user is guest
    
    # base query
    query = db.query(Event).filter(Event.archived == False)
    if rubric:
        query = query.join(EventRubric).join(Rubric).filter(Rubric.code == rubric)

    total = query.count()
    events = query.offset(offset).limit(limit).all()

    favs = set()
    tickets = set()
    if user_id:
        favs = {f.event_id for f in db.query(Favorite).filter(Favorite.user_id == user_id).all()}
        tickets = {t.event_id for t in db.query(Ticket).filter(Ticket.user_id == user_id).all()}

    results = []
    for e in events:
        results.append({
            "id": e.id,
            "title": e.title,
            "image_url": e.image_url,
            "is_favorite": e.id in favs if user_id else False,
            "is_ticket": e.id in tickets if user_id else False
        })

    return {
        "start": start,
        "pages": pages,
        "page_size": page_size,
        "total": total,
        "events": results
    }
