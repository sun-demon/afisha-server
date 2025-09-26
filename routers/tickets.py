from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Ticket, Favorite, Event, User, Rubric, EventRubric
from utils.security import get_current_user
from schemas import PaginatedEvents, EventOut


router = APIRouter(prefix="/api/tickets", tags=["tickets"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=PaginatedEvents)
def get_tickets(
    rubric: Optional[str] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(12, ge=1, le=50),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Event).filter(Event.archived == False)

    if rubric:
        query = query.join(EventRubric).join(Rubric).filter(Rubric.code == rubric)
   
    query = query.join(Ticket, Ticket.event_id == Event.id).filter(Ticket.user_id == user.id)

    total = query.count()
    events = query.offset(offset).limit(limit).all()

    event_list = [
        EventOut(
            id=e.id,
            title=e.title,
            image_url=e.image_url,
            details=e.details,
            price=e.price,
            rating=e.rating,
            archived=e.archived,
            is_ticket=True,
        )
        for e in events
    ]

    return PaginatedEvents(rubric=(rubric or "all"), offset=offset, limit=limit, total=total, events=event_list)


@router.post("/{event_id}")
def buy_ticket(
    event_id: str, 
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    if db.query(Ticket).filter_by(user_id=user.id, event_id=event_id).first():
        raise HTTPException(status_code=400, detail="Already purchased")

    ticket = Ticket(user_id=user.id, event_id=event_id)
    db.add(ticket)

    fav = db.query(Favorite).filter_by(user_id=user.id, event_id=event_id).first()
    if fav:
        db.delete(fav)

    db.commit()
    return {"message": "Ticket purchased"}
