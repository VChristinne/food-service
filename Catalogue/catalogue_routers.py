from fastapi import APIRouter, Depends, status, Request
from typing import Sequence
from sqlmodel import Session

from Catalogue.catalogue import CatalogueSchema, CatalogueModel, CatalogueUpdateSchema
from Catalogue.catalogue_service import CatalogueService
from Utils.ownership_decorator import require_roles
from main import save_log
from Database.db_config import db
from Audit.audit import AuditActionEnum
from Auth.auth import get_current_user

router = APIRouter()

def get_catalogue_service(session: Session = Depends(db.get_session)) -> CatalogueService:
    return CatalogueService(session)


@router.get("/", status_code=status.HTTP_200_OK)
@save_log(AuditActionEnum.READ, CatalogueModel)
async def get_catalogue(
        request: Request,
        service: CatalogueService = Depends(get_catalogue_service)
) -> Sequence[CatalogueModel]:
    return await service.get_all()

@router.get("/{dish_id}", status_code=status.HTTP_200_OK)
async def get_dish(
        request: Request,
        dish_id: str,
        service: CatalogueService = Depends(get_catalogue_service)
) -> CatalogueModel:
    return await service.get_by_id(dish_id)

@router.post("/", status_code=status.HTTP_201_CREATED)
@require_roles(["admin", "manager"])
@save_log(AuditActionEnum.CREATE, CatalogueModel)
async def create_dish(
        request: Request,
        catalogue_data: CatalogueSchema,
        current_user: dict = Depends(get_current_user),
        service: CatalogueService = Depends(get_catalogue_service)
) -> CatalogueModel:
    new_dish = service.create_from_schema(catalogue_data)
    return new_dish

@router.patch("/{dish_id}", status_code=status.HTTP_200_OK)
@require_roles(["admin", "manager"])
@save_log(AuditActionEnum.UPDATE, CatalogueModel)
async def update_dish(
        request: Request,
        dish_id: str,
        catalogue_data: CatalogueUpdateSchema,
        current_user: dict = Depends(get_current_user),
        service: CatalogueService = Depends(get_catalogue_service)
) -> CatalogueModel:
    updated_dish = await service.update_by_id(dish_id, catalogue_data)
    return updated_dish

@router.delete("/{dish_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_roles(["admin", "manager"])
@save_log(AuditActionEnum.DELETE, CatalogueModel)
async def delete_dish(
        request: Request,
        dish_id: str,
        current_user: dict = Depends(get_current_user),
        service: CatalogueService = Depends(get_catalogue_service)
) -> None:
    await service.delete(dish_id)
