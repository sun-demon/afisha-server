from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Event, EventRubric, Rubric, Favorite, Ticket, User
from utils.security import get_optional_user
from schemas import PaginatedEvents, EventOut


router = APIRouter(prefix="/api/events", tags=["events"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=PaginatedEvents)
def get_events(
    rubric: Optional[str] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(12, ge=1, le=50),
    id: Optional[str] = None,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    query = db.query(Event).filter(Event.archived == False)

    if id:
        ids = id.split(",")
        query = query.filter(Event.id.in_(ids))

    if rubric:
        query = query.join(EventRubric).join(Rubric).filter(Rubric.code == rubric)

    total = query.count()
    events = query.offset(offset).limit(limit).all()

    favorite_ids = (
        {f.event_id for f in db.query(Favorite.event_id).filter(Favorite.user_id == user.id).all()}
        if user else set()
    )
    ticket_ids = (
        {t.event_id for t in db.query(Ticket.event_id).filter(Ticket.user_id == user.id).all()}
        if user else set()
    )

    event_list = [
        EventOut(
            id=e.id,
            title=e.title,
            image_url=e.image_url,
            details=e.details,
            price=e.price,
            rating=e.rating,
            archived=e.archived,
            is_favorite=e.id in favorite_ids,
            is_ticket=e.id in ticket_ids,
        )
        for e in events
    ]

    return PaginatedEvents(rubric=(rubric or "all"), offset=offset, limit=limit, total=total, events=event_list)
