from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text

from common.common.core.db_config import products_engine
from api import products, auth_proxy


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with products_engine.connect() as conn:
        await conn.execute(text("SELECT 1"))

    yield


app = FastAPI(
    title="Admin Panel",
    lifespan=lifespan
)

app.include_router(products.router)
app.include_router(auth_proxy.router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}