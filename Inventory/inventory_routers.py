from fastapi import APIRouter, Depends, status, Request
from typing import Sequence
from sqlmodel import Session

from Inventory.inventory import InventorySchema, InventoryModel, InventoryUpdateSchema
from Inventory.inventory_service import InventoryService
from Utils.ownership_decorator import require_roles
from Auth.auth import get_current_user
from main import save_log
from Database.db_config import db
from Audit.audit import AuditActionEnum

router = APIRouter()

def get_inventory_service(session: Session = Depends(db.get_session)) -> InventoryService:
    return InventoryService(session)

@router.get("/", status_code=status.HTTP_200_OK)
@require_roles(["manager"])
@save_log(AuditActionEnum.READ, InventoryModel)
async def get_inventory(
    request: Request,
    current_user: dict = Depends(get_current_user),
    service: InventoryService = Depends(get_inventory_service)
) -> Sequence[InventoryModel]:
    store_id = request.state.store_id
    return await service.get_all_by_store(store_id)

@router.get("/{item_id}", status_code=status.HTTP_200_OK)
@require_roles(["manager"])
@save_log(AuditActionEnum.READ, InventoryModel)
async def get_item(
    request: Request,
    item_id: str,
    current_user: dict = Depends(get_current_user),
    service: InventoryService = Depends(get_inventory_service)
) -> InventoryModel:
    store_id = request.state.store_id
    return await service.get_by_id_and_store(item_id, store_id)

@router.post("/", status_code=status.HTTP_201_CREATED)
@require_roles(["manager"])
@save_log(AuditActionEnum.CREATE, InventoryModel)
async def create_item(
    request: Request,
    item_data: InventorySchema,
    current_user: dict = Depends(get_current_user),
    service: InventoryService = Depends(get_inventory_service)
) -> InventoryModel:
    store_id = request.state.store_id
    return service.create_for_store(item_data, store_id)

@router.patch("/{item_id}", status_code=status.HTTP_200_OK)
@require_roles(["manager"])
@save_log(AuditActionEnum.UPDATE, InventoryModel)
async def update_item(
    request: Request,
    item_id: str,
    item_data: InventoryUpdateSchema,
    current_user: dict = Depends(get_current_user),
    service: InventoryService = Depends(get_inventory_service)
) -> InventoryModel:
    store_id = request.state.store_id
    await service.validate_store_access(item_id, store_id)
    return await service.update_by_id(item_id, item_data, store_id)

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_roles(["manager"])
@save_log(AuditActionEnum.DELETE, InventoryModel)
async def delete_item(
    request: Request,
    item_id: str,
    current_user: dict = Depends(get_current_user),
    service: InventoryService = Depends(get_inventory_service)
) -> None:
    store_id = request.state.store_id
    await service.delete_by_store(item_id, store_id)
