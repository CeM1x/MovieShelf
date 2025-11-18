from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth_router import get_current_user_from_token
from src.models import Movie, Review
from src.schemas import ReviewReadSchema, ReviewCreateSchema
from src.database import SessionDep

oauth2_scheme = HTTPBearer()

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)

# -------------------- Вспомогательная функция ----------------------

async def recalc_movie_rating(movie_id: int, session: AsyncSession):
    """Пересчитывает средний рейтинг фильма по всем отзывам"""
    query_scores = select(Review.score).where(Review.movie_id == movie_id)
    result = await session.execute(query_scores)
    scores = result.scalars().all()

    new_rating = sum(scores) / len(scores) if scores else 0.0

    await session.execute(
        update(Movie)
        .where(Movie.id == movie_id)
        .values(rating=new_rating)
    )


# -------------------- Добавить отзыв ----------------------

@router.post("/add", response_model=ReviewReadSchema)
async def add_review(
    review_data: ReviewCreateSchema,
    session: SessionDep,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    token = credentials.credentials
    user = await get_current_user_from_token(token, session)
    if not user:
        raise HTTPException(status_code=401, detail="Недействительный токен")

    # VALIDATION -----
    if not 0 <= review_data.score <= 5:
        raise HTTPException(status_code=400, detail="Оценка должна быть от 0 до 5")

    movie = (await session.execute(
        select(Movie).where(Movie.id == review_data.movie_id)
    )).scalar_one_or_none()

    if not movie:
        raise HTTPException(status_code=404, detail="Фильм не найден")

    try:
        review = Review(
            text=review_data.text,
            score=review_data.score,
            movie_id=review_data.movie_id,
            user_id=user.id
        )

        session.add(review)

        # Коммитим отзыв + пересчёт рейтинга в одной транзакции
        await session.flush()  # добавили, но без коммита

        await recalc_movie_rating(movie.id, session)

        await session.commit()  # коммитим ВСЁ сразу
        await session.refresh(review)

        return review

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# -------------------- Получить все отзывы ----------------------

@router.get("/get/{movie_id}", response_model=list[ReviewReadSchema])
async def get_reviews(session: SessionDep, movie_id: int):
    movie = (await session.execute(
        select(Movie).where(Movie.id == movie_id)
    )).scalar_one_or_none()

    if not movie:
        raise HTTPException(status_code=404, detail="Фильм с таким ID не найден")

    reviews = (await session.execute(
        select(Review).where(Review.movie_id == movie_id)
    )).scalars().all()

    return reviews


# -------------------- Удалить отзыв ----------------------

@router.delete("/delete/{review_id}")
async def delete_review(
    review_id: int,
    session: SessionDep,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    token = credentials.credentials
    user = await get_current_user_from_token(token, session)
    if not user:
        raise HTTPException(status_code=401, detail="Недействительный токен")

    review = (await session.execute(
        select(Review).where(Review.id == review_id, Review.user_id == user.id)
    )).scalar_one_or_none()

    if not review:
        raise HTTPException(status_code=404, detail="Отзыв не найден или не принадлежит вам")

    movie_id = review.movie_id

    try:
        await session.delete(review)
        await session.flush()

        await recalc_movie_rating(movie_id, session)

        await session.commit()

        return {"status": "success", "message": "Отзыв удалён"}

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# -------------------- Редактировать отзыв ----------------------

@router.patch("/edit/{review_id}", response_model=ReviewReadSchema)
async def update_review(
    review_id: int,
    review_data: ReviewCreateSchema,
    session: SessionDep,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    token = credentials.credentials
    user = await get_current_user_from_token(token, session)
    if not user:
        raise HTTPException(status_code=401, detail="Недействительный токен")

    # VALIDATION -----
    if not 0 <= review_data.score <= 5:
        raise HTTPException(status_code=400, detail="Оценка должна быть от 0 до 5")

    review = (await session.execute(
        select(Review).where(Review.id == review_id, Review.user_id == user.id)
    )).scalar_one_or_none()

    if not review:
        raise HTTPException(status_code=404, detail="Отзыв не найден или не принадлежит вам")

    try:
        review.text = review_data.text
        review.score = review_data.score

        session.add(review)
        await session.flush()

        await recalc_movie_rating(review.movie_id, session)

        await session.commit()
        await session.refresh(review)

        return review

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
