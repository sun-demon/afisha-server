import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import SessionLocal
from models import User

from config import settings


router = APIRouter(prefix="/api/avatars", tags=["avatars"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{user_id}")
def get_avatar(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.avatar_url:
        raise HTTPException(status_code=404, detail="User not found")
    
    # get full path by uploads/avatars
    filepath = os.path.join(settings.UPLOAD_DIR, user.avatar_url)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Avatar file not found")
    
    return FileResponse(filepath)
