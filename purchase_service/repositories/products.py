from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from common.common.models.products import Product


class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[Product]:
        result = await self.db.execute(select(Product))
        return result.scalars().all()

    async def get_by_id(self, product_id: int) -> Product | None:
        result = await self.db.execute(select(Product).where(Product.product_id == product_id))
        return result.scalar_one_or_none()

    async def decrement_stock(self, product: Product) -> None:
        product.count_left -= 1
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)