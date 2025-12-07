from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import httpx
from http import HTTPStatus

from shared.core.db_config import AUTH_URL

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

UNAUTHORIZED = HTTPStatus.UNAUTHORIZED
BAD_GATEWAY = HTTPStatus.BAD_GATEWAY


async def verify_token_dependency(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Проверка токена через Auth-сервис.
    Возвращает payload, если токен валиден.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                AUTH_URL,
                headers={"Authorization": f"Bearer {token}"}
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=UNAUTHORIZED, detail="Invalid or expired token")
    except httpx.RequestError:
        raise HTTPException(status_code=BAD_GATEWAY, detail="Auth service unavailable")