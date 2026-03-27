from sqlmodel import Session
from uuid_extensions import uuid7

from Audit.audit import AuditModel, AuditActionEnum
from Audit.audit_repository import AuditRepository


class AuditService:
    def __init__(self, session: Session):
        self.repository = AuditRepository(session)

    def log(
            self,
            action: AuditActionEnum,
            entity: str,
            entity_id: str,
            requester_id: str,
            ip_address: str,
            router: str,
            status_code: int,
            user_agent: str
    ) -> AuditModel:
        audit = AuditModel(
            id=str(uuid7()),
            action=action,
            entity=entity,
            entity_id=entity_id,
            requester_id=requester_id,
            ip_address=ip_address,
            router=router,
            status_code=status_code,
            user_agent=user_agent
        )
        return self.repository.create(audit)
