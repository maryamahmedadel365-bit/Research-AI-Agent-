from contextlib import asynccontextmanager

import sys
import os

from fastapi import FastAPI

from src.core.db import create_tables, SessionLocal  
from src.core.scheduler import start_scheduler, stop_scheduler
from src.users.controllers import router as users_router
from src.papers.controllers import router as papers_router
from src.reading.controllers import router as reading_router
from src.users.repository import seed_users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs once on startup: creates tables and seeds the two default users."""
    import src.users.models
    import src.reading.models

    create_tables()

    db = SessionLocal()
    try:
        seed_users(db)
    finally:
        db.close()
        
    start_scheduler()

    yield  # app runs here
    
    stop_scheduler()


app = FastAPI(
    title="Research AI Agent",
    description="Research AI Agent",
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(users_router)
app.include_router(papers_router)
app.include_router(reading_router)


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)