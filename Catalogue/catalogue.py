from decimal import Decimal
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship
from uuid_extensions import uuid7

from Catalogue.dish_ingredient import DishIngredient


class CatalogueSchema(BaseModel):
    name: str
    price: Decimal = Field(max_digits=10, decimal_places=2)
    available: bool = Field(default=True)


class CatalogueModel(SQLModel, table=True):
    __tablename__ = "catalogue"

    id: str = Field(primary_key=True, default_factory=lambda: str(uuid7()))
    name: str
    price: Decimal = Field(max_digits=10, decimal_places=2)
    available: bool = Field(default=True)

    ingredients: list["InventoryModel"] = Relationship(
        back_populates="dishes", link_model=DishIngredient
    )
