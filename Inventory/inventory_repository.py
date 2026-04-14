from sqlmodel import Session

from Inventory.inventory import InventoryModel
from Utils.base_repository import BaseRepository


class InventoryRepository(BaseRepository[InventoryModel]):
    def __init__(self, session: Session):
        super().__init__(session, InventoryModel)
