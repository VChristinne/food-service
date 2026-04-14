from sqlmodel import Session

from Inventory.inventory import InventorySchema, InventoryModel
from Inventory.inventory_repository import InventoryRepository
from Utils.base_service import BaseService
from Audit.audit_service import AuditService


class InventoryService(BaseService[InventoryModel, InventorySchema, InventorySchema]):
    def __init__(self, session: Session):
        super().__init__(session, InventoryRepository, InventoryModel, "Item")
        self.audit_service = AuditService(session)
