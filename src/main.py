from fastapi import FastAPI
from src.auth_router import router as auth_router
from src.movies_router import router as movies_router


app = FastAPI()
app.include_router(auth_router)
app.include_router(movies_router)

