from fastapi import FastAPI
from contextlib import asynccontextmanager

from api import search, auth_proxy
from services.index_init import ensure_index_exists
from common.common.core.db_config import es, INDEX


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_index_exists(es=es, index=INDEX)
    yield


app = FastAPI(
    title="Product Search Service",
    lifespan=lifespan
)

app.include_router(search.router)
app.include_router(auth_proxy.router)

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}