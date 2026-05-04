from sqlmodel import Session
from uuid_extensions import uuid7

from Costumer.costumer import CostumerModel, CostumerSchema, CostumerUpdateSchema
from Costumer.costumer_repository import CostumerRepository
from Utils.base_service import BaseService
from Audit.audit_service import AuditService
from Utils.address import fetch_address
from Utils.validations import hash_password


def _handle_password(entity: CostumerModel, password: str) -> None:
    entity.password_hash = hash_password(password)


async def _handle_cep(entity: CostumerModel, cep: str) -> None:
    address = await fetch_address(cep)
    address["complement"] = entity.address.get("complement")
    entity.address = address


class CostumerService(BaseService[CostumerModel, CostumerSchema, CostumerUpdateSchema]):
    def __init__(self, session: Session):
        super().__init__(session, CostumerRepository, CostumerModel, "Customer")
        self.audit_service = AuditService(session)

    async def create_costumer(self, costumer_data: CostumerSchema) -> CostumerModel:
        address = await fetch_address(costumer_data.cep)
        address["complement"] = costumer_data.complement

        costumer = CostumerModel(
            id=str(uuid7()),
            name=costumer_data.name,
            email=costumer_data.email,
            phone=costumer_data.phone,
            password_hash=hash_password(costumer_data.password),
            address=address
        )
        return self.create(costumer)

    async def update_costumer(self, costumer_id: str, costumer_data: CostumerUpdateSchema) -> CostumerModel:
        return await self.update_by_id(
            costumer_id,
            costumer_data,
            field_handlers={
                "password": _handle_password,
                "cep": _handle_cep,
            }
        )

    async def get_all_paginated(self, page: int, page_size: int):
        """Get paginated costumers."""
        result = await self.get_paginated(page, page_size)

        return {
            "data": result["data"],
            "total": result["total"],
            "page": result["page"],
            "page_size": result["page_size"],
            "total_pages": result["total_pages"]
        }