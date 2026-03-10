from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class CatalogueSchema(BaseModel):
    id: int
    name: str
    price: Decimal = Field(max_digits=10, decimal_places=2)
    stock: int

class DishUpdateModel(BaseModel):
    id: Optional[int]
    name: Optional[str]
    price: Optional[Decimal] = Field(max_digits=10, decimal_places=2)
