from typing import Any

from fastapi import APIRouter, Depends, status, Request, Query
from sqlmodel import Session

from Catalogue.catalogue import CatalogueSchema, CatalogueModel, CatalogueUpdateSchema, PaginatedCatalogueResponse
from Catalogue.catalogue_service import CatalogueService
from Utils.ownership_decorator import require_roles
from Auth.auth import get_current_user
from main import save_log
from Database.db_config import db
from Audit.audit import AuditActionEnum

router = APIRouter()


def get_catalogue_service(session: Session = Depends(db.get_session)) -> CatalogueService:
    return CatalogueService(session)


@router.get("/{store_id}", status_code=status.HTTP_200_OK, response_model=PaginatedCatalogueResponse)
@save_log(AuditActionEnum.READ, CatalogueModel)
async def get_catalogue(
        request: Request,
        store_id: str,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
        service: CatalogueService = Depends(get_catalogue_service)
) -> dict[str, Any]:
    return await service.get_paginated_by_store(store_id, page, page_size)


@router.get("/{store_id}/{dish_id}", status_code=status.HTTP_200_OK)
@save_log(AuditActionEnum.READ, CatalogueModel)
async def get_dish(
        request: Request,
        store_id: str,
        dish_id: str,
        service: CatalogueService = Depends(get_catalogue_service)
) -> CatalogueModel:
    return await service.get_by_id_and_store(dish_id, store_id)


@router.get("/{store_id}/{dish_id}/ingredients", status_code=status.HTTP_200_OK)
@save_log(AuditActionEnum.READ, CatalogueModel)
async def get_dish_ingredients(
        request: Request,
        store_id: str,
        dish_id: str,
        service: CatalogueService = Depends(get_catalogue_service)
) -> list:
    store_id = request.state.store_id
    await service.validate_store_access(dish_id, store_id)
    return service.repository.get_ingredients_for_dish(dish_id)


@router.post("/", status_code=status.HTTP_201_CREATED)
@require_roles(["manager", "chef"])
@save_log(AuditActionEnum.CREATE, CatalogueModel)
async def create_dish(
        request: Request,
        catalogue_data: CatalogueSchema,
        current_user: dict = Depends(get_current_user),
        service: CatalogueService = Depends(get_catalogue_service)
) -> CatalogueModel:
    store_id = request.state.store_id
    return service.create_for_store(catalogue_data, store_id)


@router.patch("/{dish_id}", status_code=status.HTTP_200_OK)
@require_roles(["manager", "chef"])
@save_log(AuditActionEnum.UPDATE, CatalogueModel)
async def update_dish(
        request: Request,
        dish_id: str,
        catalogue_data: CatalogueUpdateSchema,
        current_user: dict = Depends(get_current_user),
        service: CatalogueService = Depends(get_catalogue_service)
) -> CatalogueModel:
    store_id = request.state.store_id
    await service.validate_store_access(dish_id, store_id)
    return await service.update_by_id(dish_id, catalogue_data, store_id)


@router.delete("/{dish_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_roles(["manager"])
@save_log(AuditActionEnum.DELETE, CatalogueModel)
async def delete_dish(
        request: Request,
        dish_id: str,
        current_user: dict = Depends(get_current_user),
        service: CatalogueService = Depends(get_catalogue_service)
) -> None:
    store_id = request.state.store_id
    await service.delete_by_store(dish_id, store_id)
