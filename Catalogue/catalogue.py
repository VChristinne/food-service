from decimal import Decimal
from typing import Optional
from pydantic import BaseModel
from sqlmodel import SQLModel, Field
from uuid import uuid7


class CatalogueSchema(BaseModel):
    name: str
    price: Decimal = Field(max_digits=10, decimal_places=2)
    stock: int

class DishUpdateModel(BaseModel):
    id: str
    name: Optional[str]
    price: Optional[Decimal] = Field(max_digits=10, decimal_places=2)


class CatalogueModel(SQLModel, table=True):
    __tablename__ = "catalogue"

    id: str = Field(primary_key=True, default_factory=lambda: str(uuid7()))
    name: str
    price: Decimal = Field(max_digits=10, decimal_places=2)
    stock: int
