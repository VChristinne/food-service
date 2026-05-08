from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON
from enum import Enum
from decimal import Decimal
from pydantic import BaseModel
from uuid_extensions import uuid7
from typing import Optional
from time import time


class ChannelEnum(str, Enum):
    """Onde o cliente faz o pedido."""
    APP = "app"
    TOTEM = "totem"
    COUNTER = "counter"
    WEB = "web"


class OrderTypeEnum(str, Enum):
    """Como o pedido será cumprido."""
    DINE_IN = "dine_in"
    TAKEAWAY = "takeaway"
    DELIVERY = "delivery"


class PaymentMethodEnum(str, Enum):
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    PIX = "pix"
    VALE_ALIMENTACAO = "vale_alimentacao"


class StatusEnum(str, Enum):
    PENDING = "pending"
    PREPARING = "preparing"
    TRANSIT = "transit"
    DELIVERED = "delivered"
    FAILED = "failed"


class OrderSchema(BaseModel):
    channel: ChannelEnum
    type: OrderTypeEnum
    items: list[dict]
    notes: Optional[str] = None
    payment_method: PaymentMethodEnum
    table_number: Optional[int] = None
    delivery_address: Optional[dict] = None


class OrderUpdateSchema(BaseModel):
    items: Optional[list]


class StatusUpdateSchema(BaseModel):
    status: StatusEnum


class OrderModel(SQLModel, table=True):
    __tablename__ = "orders"

    id: str = Field(primary_key=True, default_factory=lambda: str(uuid7()))
    customer_id: str = Field(foreign_key="customers.id", ondelete="CASCADE")
    store_id: str = Field(foreign_key="stores.id")
    channel: ChannelEnum
    type: OrderTypeEnum
    items: list[dict] = Field(sa_type=JSON)
    notes: Optional[str] = None
    payment_method: PaymentMethodEnum
    price: Decimal = Field(max_digits=10, decimal_places=2)
    points_earned: int
    table_number: Optional[int] = None
    delivery_address: Optional[dict] = Field(default_factory=None, sa_type=JSON)
    status: StatusEnum
    created_at: int = Field(default_factory=lambda: int(time()))
    updated_at: int = Field(default_factory=lambda: int(time()))
