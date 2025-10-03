import os, shutil
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from database import SessionLocal
from models import User
from utils.security import hash_password, verify_password, create_access_token
from config import settings
from schemas import AuthResponse, UserCreate, UserOut


router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", response_model=AuthResponse)
def register(
    username: str = Form(...),
    password: str = Form(...),
    email: Optional[str] = Form(None),
    avatar: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Username already exists"
        )
    if email and db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Email already exists"
        )

    # try:
    #     UserCreate(username=username, email=email, password=password) # type: ignore
    # except Exception as e:
    #     raise HTTPException(status_code=422, detail=str(e))

    avatar_url = None
    if avatar and avatar.filename:
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        ext = os.path.splitext(avatar.filename)[1].lower() # type: ignore
        safe_filename = f"{username}{ext}" if ext else username
        avatar_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
        with open(avatar_path, "wb") as f:
            shutil.copyfileobj(avatar.file, f)
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

    return AuthResponse(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=AuthResponse)
def login(
    login: str = Form(...),  # one field username/email
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # check, if it email (by '@')
    if "@" in login:
        user = db.query(User).filter(User.email == login).first()
    else:
        user = db.query(User).filter(User.username == login).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    return AuthResponse(access_token=token, user=UserOut.model_validate(user))
