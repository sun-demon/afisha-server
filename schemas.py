from typing import Optional, List

from pydantic import BaseModel, EmailStr, ConfigDict


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserBase(BaseModel):
    id: int
    username: str
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[EmailStr] = None


class UserOut(UserBase):
    pass


class AuthResponse(Token):
    user: UserOut


class EventOut(BaseModel):
    id: str
    title: str
    image_url: Optional[str] = None
    rating: Optional[float] = None
    price: Optional[str] = None
    details: Optional[str] = None
    archived: bool
    is_favorite: Optional[bool] = False
    is_ticket: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)


class PaginatedEvents(BaseModel):
    total: int
    offset: int
    limit: int
    events: List[EventOut]
