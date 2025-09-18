import os, shutil

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from database import SessionLocal
from models import User
from utils.security import hash_password, verify_password, create_access_token
from config import settings


router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register")
def register(username: str, password: str, email: str | None = None, avatar: UploadFile | None = File(None), db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    avatar_url = None
    if avatar:
        ext = os.path.splitext(avatar.filename)[1].lower()
        avatar_path = os.path.join(settings.UPLOAD_DIR, f"{username}{ext}")
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        with open(avatar_path, "wb") as f:
            shutil.copyfileobj(avatar.file, f)
        avatar_url = avatar_path

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        avatar_url=avatar_url
    )
    db.add(user)
    db.commit()
    return {"message": "User registered"}


@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}
