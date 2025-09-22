from typing import Optional, List

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from fastapi import Query

from database import SessionLocal
from models import Event, EventRubric, Rubric, Favorite, Ticket, User
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
    ids: Optional[List[str]] = None,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):  
    query = db.query(Event).filter(Event.archived == False)

    if ids:
        query = query.filter(Event.id.in_(ids))

    if rubric:
        query = query.join(EventRubric).join(Rubric).filter(Rubric.code == rubric)

    total = query.count()

    query = query.offset(offset).limit(limit)
    events = query.offset(offset).limit(limit).all()

    favorite_event_ids = (
        {f.event_id for f in db.query(Favorite.event_id).filter(Favorite.user_id == user.id).all()}
        if user else set()
    )
    ticket_event_ids = (
        {t.event_id for t in db.query(Ticket.event_id).filter(Ticket.user_id == user.id).all()}
        if user else set()
    )

    dict_event_list = [
        {
            "id": e.id,
            "title": e.title,
            "image_url": e.image_url,
            "details": e.details,
            "price": e.price,
            "rating": e.rating,
            "is_favorite": e.id in favorite_event_ids if user else False,
            "is_ticket": e.id in ticket_event_ids if user else False,
        }
        for e in events
    ]
    return {
        "offset": offset,
        "limit": limit,
        "total": total,
        "events": dict_event_list
    }
