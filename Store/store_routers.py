from fastapi import APIRouter, Depends, status, Query, Request
from sqlmodel import Session

from Store.store import StoreSchema, StoreModel, StoreUpdateSchema, PaginatedStoreResponse
from Store.store_service import StoreService
from Utils.ownership_decorator import require_roles
from Auth.auth import get_current_user
from main import save_log
from Database.db_config import db
from Audit.audit import AuditActionEnum

router = APIRouter()

def get_store_service(session: Session = Depends(db.get_session)) -> StoreService:
    return StoreService(session)


@router.get("/", status_code=status.HTTP_200_OK, response_model=PaginatedStoreResponse)
@require_roles(["admin"])
@save_log(AuditActionEnum.READ, StoreModel)
async def get_stores(
        request: Request,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
        current_user: dict = Depends(get_current_user),
        service: StoreService = Depends(get_store_service)
) -> PaginatedStoreResponse:
    return await service.get_all_paginated(page, page_size)

@router.get("/{store_id}", status_code=status.HTTP_200_OK)
@require_roles(["admin"])
@save_log(AuditActionEnum.READ, StoreModel)
async def get_store(
        request: Request,
        store_id: str,
        current_user: dict = Depends(get_current_user),
        service: StoreService = Depends(get_store_service)
) -> StoreModel:
    return await service.get_by_id(store_id)

@router.post("/", status_code=status.HTTP_201_CREATED)
@require_roles(["admin"])
@save_log(AuditActionEnum.CREATE, StoreModel)
async def create_store(
        request: Request,
        store_data: StoreSchema,
        current_user: dict = Depends(get_current_user),
        service: StoreService = Depends(get_store_service)
) -> StoreModel:
    return await service.create_store(store_data)

@router.patch("/{store_id}", status_code=status.HTTP_200_OK)
@require_roles(["admin"])
@save_log(AuditActionEnum.UPDATE, StoreModel)
async def update_store(
        request: Request,
        store_id: str,
        store_data: StoreUpdateSchema,
        current_user: dict = Depends(get_current_user),
        service: StoreService = Depends(get_store_service)
) -> StoreModel:
    return await service.update_store(store_id, store_data)

@router.delete("/{store_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_roles(["admin"])
@save_log(AuditActionEnum.DELETE, StoreModel)
async def delete_store(
        request: Request,
        store_id: str,
        current_user: dict = Depends(get_current_user),
        service: StoreService = Depends(get_store_service)
) -> None:
    await service.delete(store_id)
