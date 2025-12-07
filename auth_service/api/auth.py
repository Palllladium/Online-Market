from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from typing import Annotated
from http import HTTPStatus
from jwt.exceptions import InvalidTokenError

from models.user import User, UserCreate
from models.login import LoginHistory
from core.security import (
    create_access_token,
    create_refresh_token,
    validate_auth_user,
    add_to_redis_blacklist
)
from auth.utils import hash_password, decode_jwt
from repositories.auth_repository import AuthRepository

from common.core.db_config import get_auth_db, get_redis


router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


@router.post("/register", response_model=User)
async def register_user(
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_auth_db)]
):
    """
    Регистрация нового пользователя
    """
    repo = AuthRepository(db)
    existing_user = await repo.get_user_by_email(user_data.email)

    if existing_user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Email already registered"
        )

    hashed_password = hash_password(user_data.password)
    new_user = User(email=user_data.email, hashed_password=hashed_password)
    return await repo.create_user(new_user)


@router.post("/login")
async def login_user(
    db: Annotated[AsyncSession, Depends(get_auth_db)],
    user: User = Depends(validate_auth_user)
):
    """
    Залогиниться под существующим пользователем
    """
    repo = AuthRepository(db)

    access_token = create_access_token(user.email)
    refresh_token = create_refresh_token(user.email)

    login_entry = LoginHistory(
        user_id=user.id,
        user_agent=user.email or "Unknown"
    )
    await repo.add_login_history(login_entry)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh")
async def update_access_token(
    refresh_token: str,
    redis: Redis = Depends(get_redis)
):
    """
    Обновить access token у авторизованного пользователя
    """
    try:
        if await redis.exists(refresh_token):
            raise InvalidTokenError("Token revoked")

        payload = decode_jwt(refresh_token)
        if payload.get("type") != "refresh":
            raise InvalidTokenError("Invalid token type")

        new_access_token = create_access_token(payload["sub"])
        await add_to_redis_blacklist(refresh_token, payload["exp"], redis)

        return {"access_token": new_access_token}

    except InvalidTokenError as e:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post("/logout")
async def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    redis: Redis = Depends(get_redis)
):
    """
    Разлогиниться из-под авторизованного пользователя
    """
    token = credentials.credentials

    if await redis.exists(token):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Token already revoked"
        )

    payload = decode_jwt(token)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Invalid token type"
        )

    await add_to_redis_blacklist(token, payload["exp"], redis)

    return {"detail": "Logged out successfully"}