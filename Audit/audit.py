from datetime import datetime, timezone
from sqlmodel import SQLModel, Field
from pydantic import BaseModel
from enum import Enum
from uuid_extensions import uuid7


class AuditActionEnum(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"


class AuditSchema(BaseModel):
    action: AuditActionEnum
    entity: str
    entity_id: str
    user_id: str


class AuditModel(SQLModel, table=True):
    __tablename__ = "audit"

    id: str = Field(primary_key=True, default_factory=lambda: str(uuid7()))
    action: AuditActionEnum
    entity: str
    entity_id: str
    user_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
