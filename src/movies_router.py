from typing import List

from dns.e164 import query
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select

from src.schemas import MovieReadSchema, MovieAddSchema, ReviewReadSchema
from src.database import SessionDep
from src.auth_router import get_current_user_from_token
from src.models import Movie
from src.utils.tmdb import get_movie_from_tmdb

router = APIRouter(
    prefix="/movies",
    tags=["Movies"]
)

oauth2_scheme = HTTPBearer()

# ------------------- Добавить фильм -------------------

@router.post("/add", response_model=MovieReadSchema)
async def add_movie(movie_data: MovieAddSchema,
                    session: SessionDep,
                    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):

    token = credentials.credentials
    user = await get_current_user_from_token(token, session)

    if not user:
        raise HTTPException(status_code=401, detail="Недействительный или просроченный токен")

    # Проверяем есть ли такой фильм в базе
    query = select(Movie).where(Movie.tmdb_id == movie_data.tmdb_id,
                               Movie.owner_id == user.id)
    result = await session.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        return existing

    # Если не хватает данных — дополняем через TMDB
    if not movie_data.title:
        tmdb_info = await get_movie_from_tmdb(movie_data.tmdb_id)
        movie_data.title = tmdb_info["title"]
        movie_data.genre = tmdb_info["genre"]
        movie_data.description = tmdb_info["description"]


    new_movie = Movie(
        tmdb_id=movie_data.tmdb_id,
        title=movie_data.title,
        genre=movie_data.genre,
        description=movie_data.description,
        rating=movie_data.rating or 0.0,
        owner_id=user.id
    )

    session.add(new_movie)
    await session.commit()
    await session.refresh(new_movie)

    return new_movie


# ------------------- Получить фильм пользователя -------------------

@router.get("/my", response_model=List[MovieReadSchema])
async def get_my_movies(session: SessionDep, credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    token = credentials.credentials
    user = await get_current_user_from_token(token, session)

    if not user:
        raise HTTPException(status_code=401, detail="Недействительный или просроченный токен")

    query = select(Movie).where(Movie.owner_id == user.id)
    result = await session.execute(query)
    movies = result.scalars_all()

    return movies


# --------------------------- Удалить фильм -------------------------

@router.delete("/delete/{movie_id}")
async def delete_movie(movie_id: int, session: SessionDep, credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    token = credentials.credentials
    user = await get_current_user_from_token(token, session)

    if not user:
        raise HTTPException(status_code=401, detail="Недействительный или просроченный токен")

    query = select(Movie).where(Movie.owner_id == user.id,
                                Movie.id == movie_id)

    result = await session.execute(query)
    movie = result.scalar_one_or_none()

    if not movie:
        raise HTTPException(status_code=404, detail="Фильм не найден")

    await session.delete(movie)
    await session.commit()

    return {"status": "success", "message": "Movie deleted"}


# -------------------------- Обновить локальный рейтинг --------------------------

@router.patch("/{movie_id}/rate", response_model=MovieReadSchema)
async def update_rating(movie_id: int, new_rating:int,
                        session: SessionDep,
                        credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    token = credentials.credentials
    user = await get_current_user_from_token(token, session)

    if not user:
        raise HTTPException(status_code=401, detail="Недействительный или просроченный токен")

    query = select(Movie).where(Movie.id == movie_id, Movie.owner_id == user.id)
    result = await session.execute(query)
    movie = result.scalar_one_or_none()

    if not movie:
        raise HTTPException(status_code=404, detail="Фильм не найден")

    if not (0 <= new_rating <= 5):
        raise HTTPException(status_code=400, detail="Рейтинг должен быть от 0 до 5")

    movie.rating = new_rating
    await session.commit()
    await session.refresh(movie)

    return movie
