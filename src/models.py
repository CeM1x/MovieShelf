import datetime
from typing import Annotated, Optional
from sqlalchemy import String, text, Integer, CheckConstraint, ForeignKey, Float
from src.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship


intpk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]

class User(Base):
    __tablename__ = "users"

    id: Mapped[intpk]
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(250), nullable=False)
    created_at: Mapped[created_at]

    # связь "один ко многим"
    movies: Mapped[list["Movie"]] = relationship(back_populates="owner")


class Movie(Base):
    __tablename__ = "movies"
    __table_args__ = (CheckConstraint("rating >= 0.0 AND rating <= 5.0", name="rating_range"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    genre: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]]
    rating: Mapped[float] = mapped_column(Float, server_default="0.0")  # средний рейтинг

    #Внешний ключ
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["User"] = relationship(back_populates="movies")
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="movie",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[intpk]
    text: Mapped[Optional[str]]
    score: Mapped[float] = mapped_column(Float, nullable=False)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), nullable=False) # внешний ключ к фильму
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))   # внешний ключ к пользователю

    movie: Mapped["Movie"] = relationship(back_populates="reviews")
    user: Mapped["User"] = relationship()

