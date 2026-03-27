from sqlmodel import SQLModel, Field
from pydantic import BaseModel
from enum import Enum
from uuid_extensions import uuid7
from time import time


class AuditActionEnum(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"


class AuditSchema(BaseModel):
    action: AuditActionEnum
    model: str              # e.g., "costumers", "orders"
    record_id: str          # affected record
    requester_id: str       # who performed the action
    ip_address: str         # IP address of the requester
    route: str              # API endpoint accessed
    status_code: int        # HTTP status code of the response
    timestamp: int
    user_agent: str


class AuditModel(SQLModel, table=True):
    __tablename__ = "audit"

    id: str = Field(primary_key=True, default_factory=lambda: str(uuid7()))
    timestamp: int = Field(default_factory=lambda: int(time()))
    action: AuditActionEnum
    model: str
    record_id: str
    requester_id: str
    ip_address: str
    route: str
    status_code: int
    user_agent: str
