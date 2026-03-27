from typing import Sequence
from sqlmodel import Session
from fastapi import HTTPException, status
from uuid_extensions import uuid7
from fastapi import Request
from time import time

from Costumer.costumer import CostumerSchema, CostumerModel, CostumerUpdateSchema
from Costumer.costumer_repository import CostumerRepository
from Audit.audit import AuditActionEnum
from Audit.audit_service import AuditService
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
            affected_item_id=created_costumer.id,
            requester_id=created_costumer.id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            route=request.url.path,
            status_code=status_code
        )
        return created_costumer

    async def update_costumer(self, costumer_id: str, costumer_data: CostumerUpdateSchema, request: Request) -> CostumerModel:
        existing_costumer = self.repository.get_by_id(costumer_id)
        if not existing_costumer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Costumer not found")

        update_data = costumer_data.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data["password_hash"] = hash_password(update_data.pop("password"))

        if "cep" in update_data:
            address = await fetch_address(update_data.pop("cep"))
            address["complement"] = update_data.pop("complement", existing_costumer.address.get("complement"))
            update_data["address"] = address

        for field, value in update_data.items():
            setattr(existing_costumer, field, value)

        existing_costumer.updated_at = int(time())
        updated_costumer = self.repository.update(existing_costumer)

        self.audit_service.log(
            action=AuditActionEnum.UPDATE,
            model="costumers",
            affected_item_id=updated_costumer.id,
            requester_id=existing_costumer.id,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            route=request.url.path,
            status_code=200
        )
        return updated_costumer
