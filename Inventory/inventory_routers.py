from fastapi import APIRouter, Depends, status, Request
from typing import Sequence
from sqlmodel import Session

from Inventory.inventory import InventorySchema, InventoryModel
from Inventory.inventory_service import InventoryService
from Utils.ownership_decorator import require_roles
from main import save_log
from Database.db_config import db
from Audit.audit import AuditActionEnum
from Auth.auth import get_current_user

router = APIRouter()


def get_inventory_service(session: Session = Depends(db.get_session)) -> InventoryService:
    return InventoryService(session)


@router.get("/", status_code=status.HTTP_200_OK)
@require_roles(["admin", "manager"])
@save_log(AuditActionEnum.READ, InventoryModel)
async def get_inventory(
        request: Request,
        current_user: dict = Depends(get_current_user),
        service: InventoryService = Depends(get_inventory_service)
) -> Sequence[InventoryModel]:
    return await service.get_inventory()


@router.post("/", status_code=status.HTTP_201_CREATED)
@require_roles(["admin", "manager"])
@save_log(AuditActionEnum.CREATE, InventoryModel)
async def create_item(
        request: Request,
        item_data: InventorySchema,
        current_user: dict = Depends(get_current_user),
        service: InventoryService = Depends(get_inventory_service)
) -> InventoryModel:
    item = await service.create_item(item_data)
    return item


@router.patch("/{item_id}", status_code=status.HTTP_200_OK)
@require_roles(["admin", "manager"])
@save_log(AuditActionEnum.UPDATE, InventoryModel)
async def update_item(
        request: Request,
        item_id: str,
        item_data: InventorySchema,
        current_user: dict = Depends(get_current_user),
        service: InventoryService = Depends(get_inventory_service)
) -> InventoryModel:
    updated_item = await service.update_inventory(item_id, item_data)
    return updated_item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_roles(["admin", "manager"])
@save_log(AuditActionEnum.DELETE, InventoryModel)
async def delete_item(
        request: Request,
        item_id: str,
        current_user: dict = Depends(get_current_user),
        service: InventoryService = Depends(get_inventory_service)
) -> None:
    await service.delete_item(item_id, request)
