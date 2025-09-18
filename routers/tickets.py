from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi import Query

from database import SessionLocal
from models import Ticket, Favorite, Event


router = APIRouter(prefix="/api/tickets", tags=["tickets"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_tickets(
    user_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get buying user tickets with pagenation
    """
    query = db.query(Ticket).filter(Ticket.user_id == user_id)
    total = query.count()
    tickets = query.offset((page - 1) * per_page).limit(per_page).all()

    # load events
    events = [db.query(Event).get(t.event_id) for t in tickets]

    return {
        "page": page,
        "per_page": per_page,
        "total": total,
        "events": events
    }


@router.post("/{event_id}")
def buy_ticket(event_id: str, user_id: int, db: Session = Depends(get_db)):
    """
    Buy ticket (if was in favorites — remove from favorites)
    """
    if db.query(Ticket).filter_by(user_id=user_id, event_id=event_id).first():
        raise HTTPException(status_code=400, detail="Already purchased")

    ticket = Ticket(user_id=user_id, event_id=event_id)
    db.add(ticket)

    # Delete from favorites if exists
    fav = db.query(Favorite).filter_by(user_id=user_id, event_id=event_id).first()
    if fav:
        db.delete(fav)

    db.commit()
    return {"message": "Ticket purchased"}
