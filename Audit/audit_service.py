from sqlmodel import Session
from uuid_extensions import uuid7

from Audit.audit import AuditModel, AuditActionEnum
from Audit.audit_repository import AuditRepository


class AuditService:
    def __init__(self, session: Session):
        self.repository = AuditRepository(session)

    def log(self, action: AuditActionEnum, entity: str, entity_id: str, user_id: str) -> AuditModel:
        audit = AuditModel(
            id=str(uuid7()),
            action=action,
            entity=entity,
            entity_id=entity_id,
            user_id=user_id,
        )
        return self.repository.create(audit)
