from datetime import datetime as dt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from common.common.models.products import Product


async def extract_updated_products(session: AsyncSession, since: dt) -> list[Product]:
    result = await session.execute(
        select(Product).where(Product.update_time > since)
    )
    return result.scalars().all()