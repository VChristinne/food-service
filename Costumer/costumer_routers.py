from fastapi import APIRouter, Depends, status, Request, HTTPException
from typing import Sequence
from sqlmodel import Session

from Costumer.costumer import CostumerSchema, CostumerModel, CostumerUpdateSchema
from Costumer.costumer_service import CostumerService
from Utils.ownership_decorator import require_roles
from main import audit_decorator
from Database.db_config import db
from Audit.audit import AuditActionEnum
from Auth.auth import get_current_user

router = APIRouter()


def get_costumer_service(session: Session = Depends(db.get_session)) -> CostumerService:
    return CostumerService(session)


@router.get("/", status_code=status.HTTP_200_OK)
@require_roles(["admin"])
@audit_decorator.log(AuditActionEnum.READ, CostumerModel)
async def get_costumers(
        request: Request,
        current_user: dict = Depends(get_current_user),
        service: CostumerService = Depends(get_costumer_service)
) -> Sequence[CostumerModel]:
    return await service.get_costumers()


@router.post("/", status_code=status.HTTP_201_CREATED)
@audit_decorator.log(AuditActionEnum.CREATE, CostumerModel)
async def create_costumer(
        request: Request,
        costumer_data: CostumerSchema,
        service: CostumerService = Depends(get_costumer_service)
) -> CostumerModel:
    costumer = await service.create_costumer(costumer_data)
    return costumer


@router.patch("/{costumer_id}", status_code=status.HTTP_200_OK)
@require_roles(["owner"])
@audit_decorator.log(AuditActionEnum.UPDATE, CostumerModel)
async def update_costumer(
        request: Request,
        costumer_id: str,
        costumer_data: CostumerUpdateSchema,
        current_user: dict = Depends(get_current_user),
        service: CostumerService = Depends(get_costumer_service)
) -> CostumerModel:
    updated_costumer = await service.update_costumer(costumer_id, costumer_data)
    return updated_costumer
