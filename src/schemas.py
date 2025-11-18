import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, constr


# ------------------ User ------------------

class UserCreateSchema(BaseModel):
    email: EmailStr
    password: constr(min_length=4, max_length=72)  # чистый пароль, хешируется на сервере

class UserReadSchema(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime.datetime

    model_config = {
        "from_attributes": True
    } # чтобы SQLAlchemy модели могли конвертироваться в Pydantic


# ------------------ Review ------------------

class ReviewCreateSchema(BaseModel):
    text: Optional[str]
    score: float
    movie_id: int # ID фильма, к которому пишется отзыв

    model_config = {
        "from_attributes": True
    }

class ReviewReadSchema(BaseModel):
    id: int
    user_id: int
    movie_id: int
    score: float
    text: Optional[str]

    model_config = {
        "from_attributes": True
    }


# ------------------ Movie ------------------

class MovieAddCustomSchema(BaseModel):
    title: str
    genre: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = 0.0

    model_config = {"from_attributes": True}

class MovieReadSchema(BaseModel):
    id: int
    title: str
    genre: Optional[str] = None
    description: Optional[str] = None
    rating: float
    owner_id: Optional[int] = None
    reviews: list[ReviewReadSchema] = []  # просто пустой список

    model_config = {
        "from_attributes": True
    }


# ------------------ Update rating ------------------

class RatingUpdateSchema(BaseModel):
    rating: int


# ------------------ Access token ------------------

class TokenSchema(BaseModel):
    access_token: str
    token_type: str


# ------------------ Login Schema ------------------

class LoginSchema(BaseModel):
    username: str
    password: str

