from fastapi.security import OAuth2PasswordRequestForm
from flask import session
from passlib.hash import bcrypt
from jose import jwt
from fastapi import security, APIRouter, HTTPException, Depends, status
from sqlalchemy import select
from datetime import datetime, timedelta, UTC
from src.schemas import UserReadSchema, UserCreateSchema
from src.database import SessionDep
from src.models import User
from src.config import settings

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



# ------------------- Регистрация -------------------

@router.post("/register", response_model=UserReadSchema)
async def register_user(user_data: UserCreateSchema = Depends(), session: SessionDep = Depends()):
    query = (
        select(User).where(User.email == user_data.email)
    )
    result = await session.execute(query)
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    else:
        hashed_password = bcrypt.hash(user_data.password)
        user = User(email=user_data.email, password_hash=hashed_password)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

# ------------------- Авторизация -------------------

@router.post("/login")
async def login_user(form_data: OAuth2PasswordRequestForm, session: SessionDep):
    query = select(User).where(User.email == form_data.username)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Неверный email или пароль")

    if not bcrypt.verify(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Неверный email или пароль")

    payload = {"sub": str(user.id), "email": user.email}
    token = create_access_token(payload)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# добавит /me

