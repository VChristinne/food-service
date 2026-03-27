from typing import Sequence
from sqlmodel import Session
from uuid_extensions import uuid7
from fastapi import Request

from Audit.audit import AuditActionEnum
from Audit.audit_service import AuditService
from Costumer.costumer import CostumerSchema, CostumerModel
from Costumer.costumer_repository import CostumerRepository
from Utils.address import fetch_address
from Utils.validations import hash_password


class CostumerService:
    def __init__(self, session: Session):
        self.repository = CostumerRepository(session)
        self.audit_service = AuditService(session)

    async def get_costumers(self) -> Sequence[CostumerModel]:
        return self.repository.get_all()

    async def create_costumer(self, costumer_data: CostumerSchema, request: Request, status_code: int) -> CostumerModel:
        address = await fetch_address(costumer_data.cep)
        address["complement"] = costumer_data.complement

        costumer = CostumerModel(
            id=str(uuid7()),
            name=costumer_data.name,
            password_hash=hash_password(costumer_data.password),
            email=costumer_data.email,
            phone=costumer_data.phone,
            address=address
        )
        created_costumer = self.repository.create(costumer)

        self.audit_service.log(
            action=AuditActionEnum.CREATE,
            model="costumers",
            record_id=created_costumer.id,
            requester_id=created_costumer.id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            route=request.url.path,
            status_code=status_code
        )
        return created_costumer
