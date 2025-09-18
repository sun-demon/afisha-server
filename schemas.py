from typing import Optional, List

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[EmailStr] = None
    # optional client-side favorites for merging on register/login:
    client_favorites: Optional[List[str]] = None


class UserOut(BaseModel):
    id: int
    username: str
    email: Optional[EmailStr]
    avatar_url: Optional[str]

    class Config:
        orm_mode = True


class EventOut(BaseModel):
    id: str
    title: str
    image_url: Optional[str]
    rating: Optional[float]
    price: Optional[str]
    details: Optional[str]
    archived: bool
    is_favorite: Optional[bool] = False

    class Config:
        orm_mode = True


class Paginated(BaseModel):
    total: int
    page: int
    per_page: int
    items: list
