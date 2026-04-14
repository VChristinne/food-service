from sqlmodel import Session

from Audit.audit import AuditModel
from Utils.base_repository import BaseRepository


class AuditRepository(BaseRepository[AuditModel]):
    def __init__(self, session: Session):
        super().__init__(session, AuditModel)
