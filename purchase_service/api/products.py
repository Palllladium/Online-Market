from http import HTTPStatus
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import (
    APIRouter, 
    HTTPException, 
    Depends, 
    Query
)

from services.search_proxy import search_products_proxy
from services.products import (
    get_all_products,
    get_product_by_id,
    purchase_product_by_id,
)

from common.common.core.db_config import get_db
from common.common.models.products import Product
from common.common.services.auth_proxy import verify_token_dependency


router = APIRouter(prefix="/products", tags=["Products"])
NOT_FOUND = HTTPStatus.NOT_FOUND
BAD_REQUEST = HTTPStatus.BAD_REQUEST
BAD_GATEWAY = HTTPStatus.BAD_GATEWAY


@router.get("/", response_model=list[Product])
async def list_products(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_data: dict = Depends(verify_token_dependency)
):
    """
    Получение списка всех продуктов
    """
    return await get_all_products(db)


@router.get("/search")
async def search_products(
    name: str | None = Query(default=None),
    description: str | None = Query(default=None),
    user_data: dict = Depends(verify_token_dependency)
):
    """
    Поиск продуктов по названию или описанию через ElasticSearch
    """
    return await search_products_proxy(name, description)


@router.get("/{product_id}", response_model=Product)
async def get_product(
    product_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_data: dict = Depends(verify_token_dependency)
):
    """
    Получение информации о продукте по ID
    """
    product = await get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=NOT_FOUND, detail="Продукт не найден")
    return product


@router.post("/purchase/{product_id}")
async def purchase_product(
    product_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_data: dict = Depends(verify_token_dependency)
):
    """
    Покупка продукта по ID
    """
    success = await purchase_product_by_id(db, product_id)
    if not success:
        raise HTTPException(status_code=BAD_REQUEST, detail="Нельзя купить: товара нет в наличии")
    return {"status": "успешно куплено", "product_id": product_id}