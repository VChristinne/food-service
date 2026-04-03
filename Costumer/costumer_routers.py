from typing import Sequence
from sqlmodel import Session
from fastapi import APIRouter, Depends, status, Request

from Costumer.costumer import CostumerSchema, CostumerModel, CostumerUpdateSchema
from Costumer.costumer_service import CostumerService
from main import audit_decorator
from Database.db_config import db
from Audit.audit import AuditActionEnum
from Auth.auth import get_current_user

router = APIRouter()


def get_costumer_service(session: Session = Depends(db.get_session)) -> CostumerService:
    return CostumerService(session)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_costumers(service: CostumerService = Depends(get_costumer_service)) -> Sequence[CostumerModel]:
    return await service.get_costumers()


@router.post("/", status_code=status.HTTP_201_CREATED)
@audit_decorator.log(AuditActionEnum.CREATE, CostumerModel)
async def create_costumer(
        request: Request,
        client_data: CostumerSchema,
        service: CostumerService = Depends(get_costumer_service)
) -> CostumerModel:
    costumer = await service.create_costumer(client_data)
    return costumer


@router.patch("/{costumer_id}", status_code=status.HTTP_200_OK)
async def update_costumer(
        costumer_id: str,
        costumer_data: CostumerUpdateSchema,
        request: Request,
        service: CostumerService = Depends(get_costumer_service),
        current_user: dict = Depends(get_current_user)
) -> CostumerModel:
    pass
