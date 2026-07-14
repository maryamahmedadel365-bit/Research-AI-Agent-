from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.db import create_tables, SessionLocal
from users.controllers import router as users_router
from users.repository import seed_users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs once on startup: creates tables and seeds the two default users."""
    import users.models

    create_tables()

    db = SessionLocal()
    try:
        seed_users(db)
    finally:
        db.close()

    yield  # app runs here


app = FastAPI(
    title="Research AI Agent",
    description="Research AI Agent",
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(users_router)


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)