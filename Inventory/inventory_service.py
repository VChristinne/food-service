from typing import Sequence
from sqlmodel import Session
from uuid import uuid7

from Inventory.inventory import InventorySchema, InventoryModel
from Inventory.inventory_repository import InventoryRepository


class InventoryService:
    def __init__(self, session: Session):
        self.repository = InventoryRepository(session)

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
