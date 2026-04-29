from sqlalchemy import Column, JSON
from sqlmodel import SQLModel, Field
from pydantic import BaseModel, ConfigDict
from fastapi import APIRouter
from typing import Optional
from enum import Enum
from uuid_extensions import uuid7
from time import time

router = APIRouter()


class RoleEnum(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    CHEF = "chef"
    WAITER = "waiter"
    DELIVERY = "delivery"


class EmployeeSchema(BaseModel):
    name: str
    password: str
    email: str
    phone: str
    cep: str
    complement: Optional[str] = None
    role: RoleEnum


class EmployeeUpdateSchema(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    cep: Optional[str] = None
    complement: Optional[str] = None
    role: Optional[RoleEnum] = None


class EmployeeModel(SQLModel, table=True):
    __tablename__ = "employees"

    id: str = Field(primary_key=True, default_factory=lambda: str(uuid7()))
    name: str
    password_hash: str
    email: str = Field(unique=True)
    phone: str = Field(unique=True)
    address: dict = Field(sa_column=Column(JSON))
    role: RoleEnum
    created_at: int = Field(default_factory=lambda: int(time()))
    updated_at: int = Field(default_factory=lambda: int(time()))
    deleted_at: Optional[int] = None


class PaginatedEmployeeResponse(BaseModel):
    data: list[EmployeeModel]
    total: int
    page: int
    page_size: int
    total_pages: int
    model_config = ConfigDict(from_attributes=True)
