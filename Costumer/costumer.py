from sqlalchemy import Column, JSON
from sqlmodel import SQLModel, Field
from pydantic import BaseModel
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


class CostumerModel(SQLModel, table=True):
    __tablename__ = "costumers"

    id: str = Field(primary_key=True, default_factory=lambda: str(uuid7()))
    name: str
    password_hash: str
    email: str = Field(unique=True)
    phone: str = Field(unique=True)
    address: dict = Field(sa_column=Column(JSON))
    created_at: int = Field(default_factory=lambda: int(time()))
    updated_at: int = Field(default_factory=lambda: int(time()))
    deleted_at: Optional[int] = None

