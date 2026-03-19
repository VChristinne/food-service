from typing import Sequence
from sqlmodel import Session, select

from Inventory.inventory import InventoryModel


class InventoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, inventory: InventoryModel) -> InventoryModel:
        self.session.add(inventory)
        self.session.commit()
        self.session.refresh(inventory)
        return inventory

    def get_all(self) -> Sequence[InventoryModel]:
        return self.session.exec(select(InventoryModel)).all()

    def get_by_id(self, item_id: str) -> InventoryModel | None:
        return self.session.get(InventoryModel, item_id)

    def update(self, inventory: InventoryModel) -> InventoryModel:
        existing_item = self.get_by_id(inventory.id)
        if not existing_item:
            raise ValueError("Item not found")
        existing_item.name = inventory.name
        existing_item.quantity = inventory.quantity
        existing_item.unit = inventory.unit
        existing_item.min_quantity = inventory.min_quantity
        self.session.add(existing_item)
        self.session.commit()
        self.session.refresh(existing_item)
        return existing_item

    def delete(self, item_id: str) -> None:
        item = self.get_by_id(item_id)
        if item:
            self.session.delete(item)
            self.session.commit()
