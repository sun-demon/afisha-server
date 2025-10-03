import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import SessionLocal
from models import User


router = APIRouter(prefix="/api/users", tags=["users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{user_id}/avatar")
def get_avatar(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.avatar_url:
        raise HTTPException(status_code=404, detail="Avatar not found")
    
    # path to file
    filepath = user.avatar_url.lstrip("/")  # remove first '/'
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Avatar file not found")
    
    return FileResponse(filepath)
