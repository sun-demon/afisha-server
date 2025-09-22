from typing import Optional, List 

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


# Get favorites
@router.get("/")
def get_favorites(
    offset: int = Query(0, ge=0),
    limit: int = Query(12, ge=1, le=50),
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get authorized user favorite events"""
    query = (
        db.query(Event)
        .join(Favorite, Favorite.event_id == Event.id)
        .filter(Favorite.user_id == user.id)
    )  
    
    total = query.count()
    
    events = query.offset(offset).limit(limit).all()

    return {
        "offset": offset,
        "limit": limit,
        "total": total,
        "events": events
    }


# Add favorite
@router.post("/{event_id}")
def add_favorite(event_id: str, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Add event to favorites"""
    if db.query(Favorite).filter_by(user_id=current_user.id, event_id=event_id).first():
        raise HTTPException(status_code=400, detail="Already in favorites")

    fav = Favorite(user_id=current_user.id, event_id=event_id)
    db.add(fav)
    db.commit()
    return {"message": "Added to favorites"}


# Remove favorite
@router.delete("/{event_id}")
def remove_favorite(event_id: str, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete event from favorites"""
    fav = db.query(Favorite).filter_by(user_id=current_user.id, event_id=event_id).first()
    if not fav:
        raise HTTPException(status_code=404, detail="Not found")

    db.delete(fav)
    db.commit()
    return {"message": "Removed from favorites"}
