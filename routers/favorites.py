from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi import Query

from database import SessionLocal
from models import Favorite, Event


router = APIRouter(prefix="/api/favorites", tags=["favorites"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_favorites(
    user_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get user favorite events with pagenaation.
    """
    query = db.query(Favorite).filter(Favorite.user_id == user_id)
    total = query.count()
    favorites = query.offset((page - 1) * per_page).limit(per_page).all()

    # Подгружаем сами мероприятия
    events = [db.query(Event).get(f.event_id) for f in favorites]

    return {
        "page": page,
        "per_page": per_page,
        "total": total,
        "events": events
    }


@router.post("/{event_id}")
def add_favorite(event_id: str, user_id: int, db: Session = Depends(get_db)):
    """
    Add event to favorites
    """
    if db.query(Favorite).filter_by(user_id=user_id, event_id=event_id).first():
        raise HTTPException(status_code=400, detail="Already in favorites")

    fav = Favorite(user_id=user_id, event_id=event_id)
    db.add(fav)
    db.commit()
    return {"message": "Added to favorites"}


@router.delete("/{event_id}")
def remove_favorite(event_id: str, user_id: int, db: Session = Depends(get_db)):
    """
    Delete event from favorites
    """
    fav = db.query(Favorite).filter_by(user_id=user_id, event_id=event_id).first()
    if not fav:
        raise HTTPException(status_code=404, detail="Not found")

    db.delete(fav)
    db.commit()
    return {"message": "Removed from favorites"}
