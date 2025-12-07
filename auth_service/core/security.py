from jwt.exceptions import InvalidTokenError
from datetime import timedelta, datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import select
from typing import Annotated
from redis.asyncio import Redis

from common.core.db_config import (
    SETTINGS,
    get_auth_db,
    get_redis
)

from models.user import User
from auth.utils import (
    decode_jwt, 
    encode_jwt,
    validate_password
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def create_access_token(email: str) -> str:
    return encode_jwt(
        payload={
            "sub": email,
            "type": "access"
        },
        expire_minutes=SETTINGS.JWT.access_token_expire_minutes
    )


def create_refresh_token(email: str) -> str:
    return encode_jwt(
        payload={
            "sub": email,
            "type": "refresh"
        },
        expire_timedelta=timedelta(days=SETTINGS.JWT.refresh_token_expire_days)
    )


async def validate_auth_user(
    db: Annotated[AsyncSession, Depends(get_auth_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> User:
    e401 = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid username or password",
        )
    
    e403 = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User inactive",
        )
    
    email = form_data.username
    password = form_data.password

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if user is None or not validate_password(
        password=password,
        hashed_password=user.hashed_password,
    ):
        raise e401

    if not user.is_active:
        raise e403

    return user


async def get_current_token_payload(
    token: str = Depends(oauth2_scheme),
) -> dict:
    try:
        payload = decode_jwt(token=token)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token error: {e}",
        )
    
    return payload


async def get_current_auth_user(
    db: Annotated[AsyncSession, Depends(get_auth_db)],
    payload: dict = Depends(get_current_token_payload),
) -> User:
    email: str | None = payload.get("sub")
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if user is not None:
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalid (user not found)",
    )


async def get_current_active_auth_user(
    user: User = Depends(get_current_auth_user),
) -> User:
    if user.is_active:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User inactive",
    )


async def add_to_redis_blacklist(
    token: str, 
    exp_timestamp: int, 
    redis: Annotated[Redis, Depends(get_redis)]
):
    current_time = datetime.now(timezone.utc).timestamp()
    ttl = int(exp_timestamp - current_time)
    if ttl > 0:
        await redis.set(token, "revoked", ex=ttl)