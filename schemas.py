from typing import Optional, List

from pydantic import BaseModel, EmailStr, ConfigDict, field_validator


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
    email: EmailStr
    password: str

    # валидация username
    @field_validator("username")
    def validate_username(cls, v):
        if not (3 <= len(v) <= 32):
            raise ValueError("Username must be between 3 and 32 characters")
        if not v.isalnum():
            raise ValueError("Username must contain only letters and numbers")
        return v

    # валидация пароля
    @field_validator("password")
    def validate_password(cls, v):
        if len(v) < 6 or len(v) > 64:
            raise ValueError("Password must be 6–64 characters long")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        return v


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
    rubric: str
    total: int
    offset: int
    limit: int
    events: List[EventOut]
