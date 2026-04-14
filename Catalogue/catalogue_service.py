from sqlmodel import Session

from Catalogue.catalogue import CatalogueSchema, CatalogueModel, CatalogueUpdateSchema
from Catalogue.catalogue_repository import CatalogueRepository
from Utils.base_service import BaseService
from Audit.audit_service import AuditService


class CatalogueService(BaseService[CatalogueModel, CatalogueSchema, CatalogueUpdateSchema]):
    def __init__(self, session: Session):
        super().__init__(session, CatalogueRepository, CatalogueModel, "Dish")
        self.audit_service = AuditService(session)
