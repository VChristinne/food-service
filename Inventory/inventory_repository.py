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

    def get_by_id(self, item_id: int) -> InventoryModel | None:
        return self.session.get(InventoryModel, item_id)
