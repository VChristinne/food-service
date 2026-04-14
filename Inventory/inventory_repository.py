from operator import itemgetter
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

    def update(self, inventory: InventoryModel) -> InventoryModel:
        existing = self.get_by_id(inventory.id)
        if not existing:
            raise ValueError(f"Item with id {inventory.id} not found")
        self.session.add(inventory)
        self.session.commit()
        self.session.refresh(inventory)
        return inventory

    def get_all(self) -> Sequence[InventoryModel]:
        return self.session.exec(select(InventoryModel)).all()

    def get_by_id(self, item_id: str) -> InventoryModel | None:
        return self.session.get(InventoryModel, item_id)

    def delete(self, item_id: str) -> None:
        item = self.get_by_id(item_id)
        if item:
            self.session.delete(item)
            self.session.commit()
        else:
            raise ValueError(f"Item with id {item_id} not found")
