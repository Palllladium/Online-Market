from fastapi import APIRouter, Request
import httpx

from common.common.core.db_config import AUTH_URL

proxy_url = AUTH_URL.replace("user/me", "auth/login")
router = APIRouter()


@router.post("/auth/login")
async def proxy_login(request: Request):
    """
    Прокси-роут для /auth/login — нужен только для Swagger.
    """
    content = await request.body()
    headers = dict(request.headers)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            proxy_url,
            content=content,
            headers=headers
        )
    return response.json()