from sqlalchemy import Column, JSON
from sqlmodel import SQLModel, Field
from pydantic import BaseModel, ConfigDict
from fastapi import APIRouter
from typing import Optional
from uuid_extensions import uuid7
from time import time

router = APIRouter()


class CostumerSchema(BaseModel):
    name: str
    password: str
    email: str
    phone: str
    cep: str
    complement: Optional[str] = None
    orders: list = Field(default_factory=list)
    points: int = Field(default=0)


class CostumerUpdateSchema(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    cep: Optional[str] = None
    complement: Optional[str] = None
    orders: Optional[list] = None
    points: Optional[int] = None


class CostumerModel(SQLModel, table=True):
    __tablename__ = "costumers"

    id: str = Field(primary_key=True, default_factory=lambda: str(uuid7()))
    name: str
    password_hash: str
    email: str = Field(unique=True)
    phone: str = Field(unique=True)
    address: dict = Field(sa_column=Column(JSON))
    orders: list = Field(default_factory=list, sa_column=Column(JSON))
    points: int = Field(default=0)
    created_at: int = Field(default_factory=lambda: int(time()))
    updated_at: int = Field(default_factory=lambda: int(time()))
    deleted_at: Optional[int] = None


class PaginatedCostumerResponse(BaseModel):
    data: list[CostumerModel]
    total: int
    page: int
    page_size: int
    total_pages: int
    model_config = ConfigDict(from_attributes=True)
