from fastapi import FastAPI
from src.routers.auth_router import router as auth_router
from src.routers.movies_router import router as movies_router
from src.routers.reviews_router import router as reviews_router


app = FastAPI()
app.include_router(auth_router)
app.include_router(movies_router)
app.include_router(reviews_router)

