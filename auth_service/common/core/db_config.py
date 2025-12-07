from sqlalchemy.ext.asyncio import (
    AsyncSession, 
    async_sessionmaker, 
    create_async_engine
)
from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch
from shared.core.config import get_settings


SETTINGS = get_settings()

# --- CONSTANTS ---
INDEX = SETTINGS.ELASTICSEARCH_INDEX_NAME
SIZE = SETTINGS.ELASTICSEARCH_SEARCH_SIZE
INTERVAL = SETTINGS.SCHEDULE_INTERVAL_SECONDS

SEARCH_SERVICE_URL = SETTINGS.search_service_url
ELASTICSEARCH_URL = SETTINGS.elastic_search_url

PRODUCTS_POSTGRES_URL = SETTINGS.products_postgres_url
AUTH_POSTGRES_URL = SETTINGS.auth_postgres_url

AUTH_URL = SETTINGS.auth_service_url
REDIS_URL = SETTINGS.redis_url

# --- AUTH DB ---
auth_engine = create_async_engine(AUTH_POSTGRES_URL, echo=True)
AuthAsyncSessionLocal = async_sessionmaker(
    bind=auth_engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# --- PRODUCTS DB ---
products_engine = create_async_engine(PRODUCTS_POSTGRES_URL, echo=True)
ProductsAsyncSessionLocal = async_sessionmaker(
    bind=products_engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# --- Redis ---
redis = Redis.from_url(REDIS_URL)

# --- Elasticsearch ---
es = AsyncElasticsearch(hosts=[ELASTICSEARCH_URL])


# --- Dependency for FastAPI ---
def get_redis():
    return redis

async def get_auth_db() -> AsyncSession:
    async with AuthAsyncSessionLocal() as session:
        yield session

async def get_db():
    async with ProductsAsyncSessionLocal() as session:
        yield session


async def get_db_session_instance() -> AsyncSession:
    async with ProductsAsyncSessionLocal() as session:
        return session