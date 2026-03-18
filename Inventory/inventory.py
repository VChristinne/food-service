from decimal import Decimal
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship
from uuid import uuid7

from Catalogue.catalogue import CatalogueModel
from Catalogue.dish_ingredient import DishIngredient


class InventorySchema(BaseModel):
    name: str
    quantity: Decimal = Field(decimal_places=3)
    unit: str
    min_quantity: Decimal = Field(decimal_places=3)


class InventoryModel(SQLModel, table=True):
    __tablename__ = "inventory"

    id: str = Field(primary_key=True, default_factory=lambda: str(uuid7()))
    name: str
    quantity: Decimal = Field(max_digits=10, decimal_places=3)
    unit: str
    min_quantity: Decimal = Field(max_digits=10, decimal_places=3)

    dishes: list["CatalogueModel"] = Relationship(
        back_populates="ingredients", link_model=DishIngredient
    )
