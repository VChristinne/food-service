from typing import Sequence
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from Database.db_config import db
from Client.client import ClientSchema, ClientModel
from Client.client_service import ClientService

router = APIRouter()


def get_client_service(session: Session = Depends(db.get_session)) -> ClientService:
    return ClientService(session)

@router.get("/", status_code=status.HTTP_200_OK)
async def get_clients(service: ClientService = Depends(get_client_service)) -> Sequence[ClientModel]:
    return await service.get_clients()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_client(client_data: ClientSchema, service: ClientService = Depends(get_client_service)) -> dict:
    client = await service.create_client(client_data)
    return {"message": "Client created successfully", "client": client}
