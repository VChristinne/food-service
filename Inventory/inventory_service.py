from fastapi import HTTPException, status, Request
from typing import Sequence
from sqlmodel import Session
from uuid_extensions import uuid7

from Audit.audit import AuditActionEnum
from Audit.audit_service import AuditService
from Inventory.inventory import InventorySchema, InventoryModel
from Inventory.inventory_repository import InventoryRepository


class InventoryService:
    def __init__(self, session: Session):
        self.repository = InventoryRepository(session)
        self.audit_service = AuditService(session)

    async def get_inventory(self) -> Sequence[InventoryModel]:
        return self.repository.get_all()

    async def create_item(self, item_data: InventorySchema, request: Request, status_code: int) -> InventoryModel:
        item = InventoryModel(
            id=str(uuid7()),
            name=item_data.name,
            quantity=item_data.quantity,
            unit=item_data.unit,
            min_quantity=item_data.min_quantity,
        )
        created_item = self.repository.create(item)

        self.audit_service.log(
            action=AuditActionEnum.CREATE,
            model="inventory",
            affected_item_id=created_item.id,
            requester_id="system",  # TODO: Change to emplyeeid when implemented
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            route=request.url.path,
            status_code=status_code
        )
        return created_item

    async def update_inventory(self, item_id: str, item_data: InventorySchema, request: Request) -> InventoryModel:
        item = self.repository.get_by_id(item_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        item.name = item_data.name
        item.quantity = item_data.quantity
        item.unit = item_data.unit
        item.min_quantity = item_data.min_quantity
        updated_item = self.repository.create(item)

        self.audit_service.log(
            action=AuditActionEnum.UPDATE,
            model="inventory_item",
            affected_item_id=updated_item.id,
            requester_id="system",  # TODO: Change to emplyeeid when implemented
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            route=request.url.path,
            status_code=status.HTTP_200_OK
        )
        return updated_item

    async def delete_item(self, item_id: str, request: Request) -> None:
        try:
            self.repository.get_by_id(item_id)
        except:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        finally:
            self.audit_service.log(
                action=AuditActionEnum.DELETE,
                model="inventory_item",
                affected_item_id=item_id,
                requester_id="system",  # TODO: Change to emplyeeid when implemented
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent"),
                route=request.url.path,
                status_code=status.HTTP_204_NO_CONTENT
            )
            self.repository.delete(item_id)
