from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from sqlalchemy import text

from common.core.db_config import auth_engine, redis
from api import auth, users

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with auth_engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    
    await redis.ping()
    
    async with auth_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    yield

app = FastAPI(
    title="Auth service",
    lifespan=lifespan
)

app.include_router(auth.router)
app.include_router(users.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}