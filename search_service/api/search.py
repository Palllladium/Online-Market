from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    Depends
)
from http import HTTPStatus

from services.search import search_products
from common.common.services.auth_proxy import verify_token_dependency


router = APIRouter(prefix="/search", tags=["Search"])
BAD_REQUEST = HTTPStatus.BAD_REQUEST
BAD_GATEWAY = HTTPStatus.BAD_GATEWAY


@router.get("/")
async def search(
    name: str | None = Query(None),
    description: str | None = Query(None),
    user_data: dict = Depends(verify_token_dependency)
):
    if not name and not description:
        raise HTTPException(
            status_code=BAD_REQUEST,
            detail="Нужно указать name или description"
        )

    try:
        results = await search_products(name, description)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=BAD_GATEWAY,
            detail=f"Ошибка поиска: {str(e)}"
        )