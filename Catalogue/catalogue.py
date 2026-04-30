from decimal import Decimal
from typing import Optional
from time import time

from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship
from uuid_extensions import uuid7

from Catalogue.dish_ingredient import DishIngredient


class CatalogueSchema(BaseModel):
    name: str
    price: Decimal = Field(max_digits=10, decimal_places=2)
    available: bool = Field(default=True)
    store_id: Optional[str] = None


class CatalogueUpdateSchema(BaseModel):
    name: Optional[str] = None
    price: Optional[Decimal] = Field(max_digits=10, decimal_places=2)
    available: Optional[bool] = Field(default=True)


class CatalogueModel(SQLModel, table=True):
    __tablename__ = "catalogue"

    id: str = Field(primary_key=True, default_factory=lambda: str(uuid7()))
    name: str
    price: Decimal = Field(max_digits=10, decimal_places=2)
    available: bool = Field(default=True)
    store_id: Optional[str] = Field(default=None, foreign_key="stores.id")
    ingredients: list["InventoryModel"] = Relationship(  # noqa
        back_populates="dishes", link_model=DishIngredient
    )
    created_at: int = Field(default_factory=lambda: int(time()))
    updated_at: int = Field(default_factory=lambda: int(time()))
    deleted_at: Optional[int] = None
