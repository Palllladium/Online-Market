from sqlmodel import (
    SQLModel, 
    Text, 
    DateTime, 
    Field
)
from typing import Optional
from pydantic import ConfigDict
from datetime import datetime as dt, timezone


class ProductBase(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    product_name: str = Field(max_length=100)
    product_description: str = Field(sa_type=Text)
    count_left: int = Field(ge=0)


class ProductCreate(ProductBase):
    pass


class Product(ProductBase, table=True):
    __tablename__ = "products"

    product_id: Optional[int] = Field(default=None, primary_key=True)
    create_time: dt = Field(
        default_factory=lambda: dt.now(timezone.utc),
        sa_type=DateTime(timezone=True)
    )
    update_time: dt = Field(
        default_factory=lambda: dt.now(timezone.utc),
        sa_type=DateTime(timezone=True)
    )


class ProductUpdate(SQLModel):
    product_name: Optional[str] = Field(
        None,
        description="Новое название продукта"
    )
    product_description: Optional[str] = Field(
        None,
        description="Новое описание продукта"
    )
    count_left: Optional[int] = Field(
        None,
        ge=0,
        description="Количество товара на складе"
    )