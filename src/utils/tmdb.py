import aiohttp
from src.config import settings

TMDB_URL = "https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={api_key}&language=en-US"

async def get_movie_from_tmdb(tmdb_id: int):
    url = TMDB_URL.format(tmdb_id=tmdb_id , api_key=settings.TMDB_API_KEY)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise ValueError("TMDB: movie not found")

            data = await resp.json()

            return {
                "title": data.get("title"),
                "genre": data["genres"][0]["name"] if data.get("genres") else None,
                "description": data.get("overview")
            }