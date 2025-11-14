from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.hash import bcrypt
from jose import jwt, JWTError
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select
from datetime import datetime, timedelta, UTC
from src.schemas import UserReadSchema, UserCreateSchema, TokenSchema, LoginSchema
from src.database import SessionDep
from src.models import User
from src.config import settings, SECRET_KEY, ALGORITHM


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


# ------------------- Создание токена доступа -------------------

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ------------------- Регистрация -------------------

@router.post("/register", response_model=UserReadSchema)
async def register_user(user_data: UserCreateSchema, session: SessionDep):
    query = select(User).where(User.email == user_data.email)
    result = await session.execute(query)
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    else:
        hashed_password = bcrypt.hash(user_data.password[:72])
        user = User(email=user_data.email, password_hash=hashed_password)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

# ------------------- Авторизация -------------------

@router.post("/login", response_model=TokenSchema)
async def login_user(session: SessionDep, form_data: LoginSchema):
    query = select(User).where(User.email == form_data.username)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Неверный email или пароль")

    if not bcrypt.verify(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Неверный email или пароль")

    payload = {"sub": user.email}
    token = create_access_token(payload)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ------------------- Получение текущего пользователя -------------------

oauth2_scheme = HTTPBearer()

async def get_current_user_from_token(token: str, session: SessionDep):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])

        email: str = payload.get("sub")
        if email is None:
            return None

    except JWTError:
        return None

    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    return user


@router.get("/me", response_model=UserReadSchema)
async def get_me(session: SessionDep, credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    token = credentials.credentials
    user = await get_current_user_from_token(token, session)

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user


