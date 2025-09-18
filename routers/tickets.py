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
    offset: int = Query(0, ge=0),
    limit: int = Query(12, ge=1, le=50),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get buying user tickets with pagenation
    """
    query = db.query(Ticket).filter(Ticket.user_id == current_user.id)
    total = query.count()
    tickets = query.offset(offset).limit(limit).all()

    # load events
    events = [db.query(Event).get(t.event_id) for t in tickets]

    return {
        "offset": offset,
        "limit": limit,
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
