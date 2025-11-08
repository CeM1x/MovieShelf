from fastapi import FastAPI
import uvicorn

TMDB_API_KEY = "aab9cf87d0dfbc12ed70987d48a92cc0"
TMDB_ACCESS_API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhYWI5Y2Y4N2QwZGZiYzEyZWQ3MDk4N2Q0OGE5MmNjMCIsIm5iZiI6MTc2MjYwMTU3Mi42MjUsInN1YiI6IjY5MGYyYTY0YTVlZjA2YjhkMjRjNzc4ZCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.s9eVd7r9unatq1i7eBRqtGzBv6I0WheYm1QB0jvZrig"

app = FastAPI()


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)