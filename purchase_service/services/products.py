from sqlalchemy.ext.asyncio import AsyncSession

from common.common.models.products import Product
from repositories.products import ProductRepository


async def get_all_products(db: AsyncSession) -> list[Product]:
    return await ProductRepository(db).get_all()


async def get_product_by_id(db: AsyncSession,  product_id: int) -> Product | None:
    return await ProductRepository(db).get_by_id(product_id)


async def purchase_product_by_id(db: AsyncSession,  product_id: int) -> bool:
    db_instance = ProductRepository(db)
    product = await db_instance.get_by_id(product_id)
    if not product or product.count_left <= 0:
        return False
    else:
        await db_instance.decrement_stock(product)
        return True