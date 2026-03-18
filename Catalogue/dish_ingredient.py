from decimal import Decimal
from pydantic import BaseModel
from sqlmodel import SQLModel, Field


class DishIngredientSchema(BaseModel):
    dish_id: str
    ingredient_id: str
    quantity: Decimal = Field(max_digits=10, decimal_places=3)


class DishIngredient(SQLModel, table=True):
    __tablename__ = "dish_ingredient"

    dish_id: str = Field(foreign_key="catalogue.id", primary_key=True)
    ingredient_id: str = Field(foreign_key="inventory.id", primary_key=True)
    quantity: Decimal = Field(max_digits=10, decimal_places=3)
