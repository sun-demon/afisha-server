from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi import Query

from database import SessionLocal
from models import Favorite, Event
from utils.security import get_current_user


router = APIRouter(prefix="/api/favorites", tags=["favorites"])


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Get favorites (paginated)
@router.get("/")
def get_favorites(
    start: int = Query(1, ge=1),
    pages: int = Query(1, ge=1),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user favorite events with pagenaation.
    """
    page_size = 12
    query = db.query(Favorite).filter(Favorite.user_id == current_user.id)
    total = query.count()
    favorites = query.offset((start - 1) * page_size).limit(pages * page_size).all()

    # load events
    events = [db.query(Event).get(f.event_id) for f in favorites]

    return {
        "start": start,
        "pages": pages,
        "page_size": page_size,
        "total": total,
        "events": events
    }


# Add favorite
@router.post("/{event_id}")
def add_favorite(event_id: str, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Add event to favorites
    """
    if db.query(Favorite).filter_by(user_id=current_user.id, event_id=event_id).first():
        raise HTTPException(status_code=400, detail="Already in favorites")

    fav = Favorite(user_id=current_user.id, event_id=event_id)
    db.add(fav)
    db.commit()
    return {"message": "Added to favorites"}


# Remove favorite
@router.delete("/{event_id}")
def remove_favorite(event_id: str, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Delete event from favorites
    """
    fav = db.query(Favorite).filter_by(user_id=current_user.id, event_id=event_id).first()
    if not fav:
        raise HTTPException(status_code=404, detail="Not found")

    db.delete(fav)
    db.commit()
    return {"message": "Removed from favorites"}
