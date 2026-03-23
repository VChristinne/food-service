from typing import Sequence
from uuid_extensions import uuid7
from sqlmodel import Session

from Audit.audit import AuditActionEnum
from Audit.audit_service import AuditService
from Catalogue.catalogue import CatalogueSchema, CatalogueModel
from Catalogue.catalogue_repository import CatalogueRepository


class CatalogueService:
    def __init__(self, session: Session):
        self.repository = CatalogueRepository(session)
        self.audit_service = AuditService(session)

    async def get_catalogue(self) -> Sequence[CatalogueModel]:
        return self.repository.get_all()

    async def create_dish(self, catalogue_data: CatalogueSchema) -> CatalogueModel:
        dish = CatalogueModel(
            id=str(uuid7()),
            name=catalogue_data.name,
            price=catalogue_data.price,
            available=catalogue_data.available
        )
        created_dish = self.repository.create(dish)

        self.audit_service.log(
            action=AuditActionEnum.CREATE,
            entity="catalogue",
            entity_id=created_dish.id,
            user_id="system"  # TODO: Change to employee id when implemented
        )
        return created_dish

    async def update_dish(self, dish_id, update_data):
        pass

    async def delete_dish(self, dish_id):
        pass