from typing import Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from fastapi import Query

from database import SessionLocal
from models import Event, EventRubric, Rubric, Favorite, Ticket
from utils.security import get_optional_user


router = APIRouter(prefix="/api/events", tags=["events"])


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_events(
    rubric: Optional[str] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(12, ge=1, le=50),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
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
        "offset": offset,
        "limit": limit,
        "total": total,
        "events": results
    }
