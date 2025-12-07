from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from http import HTTPStatus

from models.user import User, UserUpdate
from models.login import LoginHistory
from auth.utils import hash_password
from core.security import get_current_active_auth_user, get_current_token_payload
from repositories.user_repository import UserRepository

from common.common.core.db_config import get_auth_db


router = APIRouter(prefix="/user", tags=["user"])


@router.put("/update", response_model=User)
async def update_user_data(
    update_data: UserUpdate,
    db: AsyncSession = Depends(get_auth_db),
    current_user: User = Depends(get_current_active_auth_user)
):
    """
    Обновить информацию об авторизованном пользователе
    """
    repo = UserRepository(db)

    if update_data.email:
        existing_user = await repo.get_user_by_email(update_data.email)
        if existing_user:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = update_data.email

    if update_data.password:
        current_user.hashed_password = hash_password(update_data.password)

    return await repo.update_user(current_user)


@router.get("/history", response_model=List[LoginHistory])
async def get_login_history(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_auth_db),
    current_user: User = Depends(get_current_active_auth_user)
):
    """
    Получить историю логинов авторизованного пользователя
    """
    repo = UserRepository(db)
    return await repo.get_login_history(current_user.id, skip, limit)


@router.get("/me")
async def auth_user_check_self_info(
    payload: dict = Depends(get_current_token_payload),
    user: User = Depends(get_current_active_auth_user),
):
    """
    Получить информацию об авторизованном пользователе
    """
    return {
        "email": user.email,
        "logged_in_at": payload.get("iat"),
    }