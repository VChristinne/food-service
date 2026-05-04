from sqlalchemy import Column, JSON
from sqlmodel import SQLModel, Field
from pydantic import BaseModel, ConfigDict
from uuid_extensions import uuid7
from typing import Optional
from time import time


class StoreSchema(BaseModel):
    phone: str
    cep: str
    complement: Optional[str] = None


class StoreUpdateSchema(BaseModel):
    phone: Optional[str] = None
    cep: Optional[str] = None
    complement: Optional[str] = None


class StoreModel(SQLModel, table=True):
    __tablename__ = "stores"

    id: str = Field(primary_key=True, default_factory=lambda: str(uuid7()))
    phone: str
    address: dict = Field(sa_column=Column(JSON))
    created_at: int = Field(default_factory=lambda: int(time()))
    updated_at: int = Field(default_factory=lambda: int(time()))
    deleted_at: Optional[int] = None


class PaginatedStoreResponse(BaseModel):
    data: list[StoreModel]
    total: int
    page: int
    page_size: int
    total_pages: int
    model_config = ConfigDict(from_attributes=True)
