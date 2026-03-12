from datetime import datetime, timezone
from sqlalchemy import Column, JSON
from sqlmodel import SQLModel, Field
from pydantic import BaseModel
from fastapi import APIRouter
from typing import Optional
from uuid import uuid7

router = APIRouter()


class ClientSchema(BaseModel):
    name: str
    password: str
    email: str
    phone: str
    cep: str
    complement: Optional[str] = None


class ClientModel(SQLModel, table=True):
    __tablename__ = "client"

    id: str = Field(primary_key=True, default_factory=lambda: str(uuid7()))
    name: str
    password_hash: str
    email: str = Field(unique=True)
    phone: str = Field(unique=True)
    address: dict = Field(sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    deleted_at: Optional[datetime] = None
