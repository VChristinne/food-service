from sqlmodel import Session
from uuid_extensions import uuid7

from Customer.customer import CustomerModel, CustomerSchema, CustomerUpdateSchema
from Customer.customer_repository import CustomerRepository
from Utils.base_service import BaseService
from Audit.audit_service import AuditService
from Utils.address import fetch_address
from Utils.validations import hash_password


def _handle_password(entity: CustomerModel, password: str) -> None:
    entity.password_hash = hash_password(password)


async def _handle_cep(entity: CustomerModel, cep: str) -> None:
    address = await fetch_address(cep)
    address["complement"] = entity.address.get("complement")
    entity.address = address


class CustomerService(BaseService[CustomerModel, CustomerSchema, CustomerUpdateSchema]):
    def __init__(self, session: Session):
        super().__init__(session, CustomerRepository, CustomerModel, "Customer")
        self.audit_service = AuditService(session)

    async def create_customer(self, customer_data: CustomerSchema) -> CustomerModel:
        address = await fetch_address(customer_data.cep)
        address["complement"] = customer_data.complement

        customer = CustomerModel(
            id=str(uuid7()),
            name=customer_data.name,
            email=customer_data.email,
            phone=customer_data.phone,
            password_hash=hash_password(customer_data.password),
            address=address
        )
        return self.create(customer)

    async def update_customer(self, customer_id: str, customer_data: CustomerUpdateSchema) -> CustomerModel:
        return await self.update_by_id(
            customer_id,
            customer_data,
            field_handlers={
                "password": _handle_password,
                "cep": _handle_cep,
            }
        )

    async def get_all_paginated(self, page: int, page_size: int):
        """Get paginated customers."""
        result = await self.get_paginated(page, page_size)

        return {
            "data": result["data"],
            "total": result["total"],
            "page": result["page"],
            "page_size": result["page_size"],
            "total_pages": result["total_pages"]
        }
