from fastapi import APIRouter, Depends, status, Request, Query
from typing import Sequence
from sqlmodel import Session

from Costumer.costumer import CostumerSchema, CostumerModel, CostumerUpdateSchema, PaginatedCostumerResponse
from Costumer.costumer_service import CostumerService
from Utils.ownership_decorator import require_roles
from main import save_log
from Database.db_config import db
from Audit.audit import AuditActionEnum
from Auth.auth import get_current_user

router = APIRouter()

def get_costumer_service(session: Session = Depends(db.get_session)) -> CostumerService:
    return CostumerService(session)


@router.get("/", status_code=status.HTTP_200_OK, response_model=PaginatedCostumerResponse)
@require_roles(["admin"])
@save_log(AuditActionEnum.READ, CostumerModel)
async def get_costumers(
        request: Request,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(10, ge=1, description="Number of items per page"),
        current_user: dict = Depends(get_current_user),
        service: CostumerService = Depends(get_costumer_service)
) -> PaginatedCostumerResponse:
    return await service.get_all_paginated(page, page_size)

@router.get("/{costumer_id}", status_code=status.HTTP_200_OK)
@require_roles(["admin"])
@save_log(AuditActionEnum.READ, CostumerModel)
async def get_costumer(
        request: Request,
        costumer_id: str,
        current_user: dict = Depends(get_current_user),
        service: CostumerService = Depends(get_costumer_service)
) -> CostumerModel:
    return await service.get_by_id(costumer_id)

@router.post("/", status_code=status.HTTP_201_CREATED)
@save_log(AuditActionEnum.CREATE, CostumerModel)
async def create_costumer(
        request: Request,
        costumer_data: CostumerSchema,
        service: CostumerService = Depends(get_costumer_service)
) -> CostumerModel:
    new_costumer = await service.create_costumer(costumer_data)
    return new_costumer

@router.patch("/{costumer_id}", status_code=status.HTTP_200_OK)
@require_roles(["owner"])
@save_log(AuditActionEnum.UPDATE, CostumerModel)
async def update_costumer(
        request: Request,
        costumer_id: str,
        costumer_data: CostumerUpdateSchema,
        current_user: dict = Depends(get_current_user),
        service: CostumerService = Depends(get_costumer_service)
) -> CostumerModel:
    updated_costumer = await service.update_by_id(costumer_id, costumer_data)
    return updated_costumer
