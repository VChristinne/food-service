from typing import Sequence
from sqlmodel import Session, select

from Audit.audit import AuditModel


class AuditRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, audit: AuditModel) -> AuditModel:
        self.session.add(audit)
        self.session.commit()
        self.session.refresh(audit)
        return audit

    def get_all(self) -> Sequence[AuditModel]:
        return self.session.exec(select(AuditModel)).all()

    def get_by_id(self, audit_id: str) -> AuditModel | None:
        return self.session.get(AuditModel, audit_id)
