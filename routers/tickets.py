from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi import Query

from database import SessionLocal
from models import Ticket, Favorite, Event
from utils.security import get_current_user


router = APIRouter(prefix="/api/tickets", tags=["tickets"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_tickets(
    start: int = Query(1, ge=1),
    pages: int = Query(1, ge=1),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get buying user tickets with pagenation
    """
    page_size = 12
    query = db.query(Ticket).filter(Ticket.user_id == current_user.id)
    total = query.count()
    tickets = query.offset((start - 1) * page_size).limit(pages * page_size).all()

    # load events
    events = [db.query(Event).get(t.event_id) for t in tickets]

    return {
        "start": start,
        "pages": pages,
        "page_size": page_size,
        "total": total,
        "events": events
    }


@router.post("/{event_id}")
def buy_ticket(event_id: str, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Buy ticket (if was in favorites — remove from favorites)
    """
    if db.query(Ticket).filter_by(user_id=current_user.id, event_id=event_id).first():
        raise HTTPException(status_code=400, detail="Already purchased")

    ticket = Ticket(user_id=current_user.id, event_id=event_id)
    db.add(ticket)

    # Delete from favorites if exists
    fav = db.query(Favorite).filter_by(user_id=current_user.id, event_id=event_id).first()
    if fav:
        db.delete(fav)

    db.commit()
    return {"message": "Ticket purchased"}
