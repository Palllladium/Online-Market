from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime as dt, timezone

from common.common.models.products import (
    Product, 
    ProductCreate, 
    ProductUpdate
)


async def create_product(db: AsyncSession, product: ProductCreate) -> Product:
    new_product = Product(**product.model_dump())
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product


async def update_product(db: AsyncSession, product_id: int, product: ProductUpdate) -> Product | None:
    result = await db.execute(select(Product).where(Product.product_id == product_id))
    db_product = result.scalar_one_or_none()
    if not db_product:
        return None

    update_data = product.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)

    db_product.update_time = dt.now(timezone.utc)

    await db.commit()
    await db.refresh(db_product)
    return db_product