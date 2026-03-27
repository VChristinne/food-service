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
            model: str,
            affected_item_id: str,
            requester_id: str,
            ip_address: str,
            route: str,
            status_code: int,
            user_agent: str
    ) -> AuditModel:
        audit = AuditModel(
            id=str(uuid7()),
            action=action,
            model=model,
            affected_item_id=affected_item_id,
            requester_id=requester_id,
            ip_address=ip_address,
            route=route,
            status_code=status_code,
            user_agent=user_agent
        )
        return self.repository.create(audit)
