from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter

router = APIRouter()


class ClientSchema(BaseModel):
    name: str
    password: str
    email: str
    phone: str
    cep: str
    complement: Optional[str] = None
