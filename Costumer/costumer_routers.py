from typing import Sequence
from sqlmodel import Session
from fastapi import APIRouter, Depends, status, Request

from Database.db_config import db
from Costumer.costumer_service import CostumerService
from Costumer.costumer import CostumerSchema, CostumerModel

router = APIRouter()


def get_costumer_service(session: Session = Depends(db.get_session)) -> CostumerService:
    return CostumerService(session)

@router.get("/", status_code=status.HTTP_200_OK)
async def get_costumers(service: CostumerService = Depends(get_costumer_service)) -> Sequence[CostumerModel]:
    return await service.get_costumers()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_costumer(request: Request, client_data: CostumerSchema, service: CostumerService = Depends(get_costumer_service)) -> dict:
    costumer = await service.create_costumer(client_data, request, status.HTTP_201_CREATED)
    return {"message": "Costumer created successfully", "client": {"id": costumer.id}}
