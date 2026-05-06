from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from decimal import Decimal
from pydantic import BaseModel
from uuid_extensions import uuid7
from typing import Optional
from time import time

from Catalogue.dish_ingredient import DishIngredient


class UnitEnum(str, Enum):
    GRAMS = "g"
    MILLILITERS = "ml"
    UNITS = "un"


class InventorySchema(BaseModel):
    name: str
    quantity: Decimal = Field(decimal_places=3)
    unit: UnitEnum
    min_quantity: Decimal = Field(decimal_places=3)
    store_id: str


class InventoryUpdateSchema(BaseModel):
    name: Optional[str] = None
    quantity: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=3)
    unit: Optional[UnitEnum] = None
    min_quantity: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=3)


class InventoryModel(SQLModel, table=True):
    __tablename__ = "inventory"

    id: str = Field(primary_key=True, default_factory=lambda: str(uuid7()))
    name: str
    quantity: Decimal = Field(max_digits=10, decimal_places=3)
    unit: UnitEnum
    min_quantity: Decimal = Field(max_digits=10, decimal_places=3)
    store_id: Optional[str] = Field(default=None, foreign_key="stores.id")
    dishes: list["CatalogueModel"] = Relationship(     # noqa
        back_populates="ingredients", link_model=DishIngredient
    )
    created_at: int = Field(default_factory=lambda: int(time()))
    updated_at: int = Field(default_factory=lambda: int(time()))
    deleted_at: Optional[int] = None
