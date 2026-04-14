from fastapi import HTTPException, status, Request
from typing import Sequence
from sqlmodel import Session
from uuid_extensions import uuid7
from time import time

from Inventory.inventory import InventorySchema, InventoryModel
from Inventory.inventory_repository import InventoryRepository
from Audit.audit_service import AuditService


class InventoryService:
    def __init__(self, session: Session):
        self.repository = InventoryRepository(session)
        self.audit_service = AuditService(session)

    async def get_inventory(self) -> Sequence[InventoryModel]:
        return self.repository.get_all()

    async def create_item(self, item_data: InventorySchema) -> InventoryModel:
        item = InventoryModel(
            id=str(uuid7()),
            name=item_data.name,
            quantity=item_data.quantity,
            unit=item_data.unit,
            min_quantity=item_data.min_quantity,
        )
        return self.repository.create(item)

    async def update_inventory(self, item_id: str, item_data: InventorySchema) -> InventoryModel:
        existing_item = self.repository.get_by_id(item_id)
        if not existing_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

        update_data = item_data.model_dump(exclude_unset=True)

        for field in list(update_data.keys()):
            match field:
                case "name":
                    existing_item.name = update_data["name"]
                case "quantity":
                    existing_item.quantity = update_data["quantity"]
                case "unit":
                    existing_item.unit = update_data["unit"]
                case "min_quantity":
                    existing_item.min_quantity = update_data["min_quantity"]

        update_data["updated_at"] = int(time())
        return self.repository.update(existing_item)

    async def delete_item(self, item_id: str, request: Request) -> None:
        existing_item = self.repository.get_by_id(item_id)
        if not existing_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        self.repository.delete(item_id)
