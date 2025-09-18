import os, shutil
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from database import SessionLocal
from models import User
from utils.security import hash_password, verify_password, create_access_token
from config import settings


router = APIRouter(prefix="/api/auth", tags=["auth"])


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Register user
@router.post("/register")
def register(
    username: str,
    password: str,
    email: Optional[str] = None,
    avatar: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
) -> dict:
    """Register a new user with optional avatar upload"""
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    avatar_url = None
    if avatar:
        # create directory if needed
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

        # safely filename
        ext = os.path.splitext(avatar.filename)[1].lower()
        safe_filename = f"{username}{ext}"
        avatar_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

        # save file
        with open(avatar_path, "wb") as f:
            shutil.copyfileobj(avatar.file, f)

        # save path for API
        avatar_url = f"/{settings.UPLOAD_DIR.rstrip('/')}/{safe_filename}"

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        avatar_url=avatar_url
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})

    return {
        "message": "User registered",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar_url": user.avatar_url
        }
    }


@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)) -> dict:
    """Authenticate user and return JWT"""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar_url": user.avatar_url
        }
    }