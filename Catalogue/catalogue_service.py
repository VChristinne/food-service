from typing import Sequence
from uuid_extensions import uuid7
from sqlmodel import Session
from fastapi import Request

from Audit.audit import AuditActionEnum
from Audit.audit_service import AuditService
from Catalogue.catalogue import CatalogueSchema, CatalogueModel
from Catalogue.catalogue_repository import CatalogueRepository
from Utils.validations import sanitize_user_agent


class CatalogueService:
    def __init__(self, session: Session):
        self.repository = CatalogueRepository(session)
        self.audit_service = AuditService(session)

    async def get_catalogue(self) -> Sequence[CatalogueModel]:
        return self.repository.get_all()

    async def create_dish(self, catalogue_data: CatalogueSchema, request: Request, status_code: int) -> CatalogueModel:
        dish = CatalogueModel(
            id=str(uuid7()),
            name=catalogue_data.name,
            price=catalogue_data.price,
            available=catalogue_data.available
        )
        created_dish = self.repository.create(dish)

        self.audit_service.log(
            action=AuditActionEnum.CREATE,
            model="catalogue",
            record_id=created_dish.id,
            requester_id="system",
            ip_address=request.client.host,
            user_agent=sanitize_user_agent(request.headers.get("User-Agent")),
            route=request.url.path,
            status_code=status_code
        )
        return created_dish

    async def update_dish(self, dish_id, update_data):
        pass

    async def delete_dish(self, dish_id):
        pass