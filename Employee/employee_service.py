from sqlmodel import Session
from uuid_extensions import uuid7
from math import ceil

from Employee.employee import EmployeeSchema, EmployeeModel, EmployeeUpdateSchema, PaginatedEmployeeResponse
from Employee.employee_repository import EmployeeRepository
from Utils.base_service import BaseService
from Audit.audit_service import AuditService
from Utils.address import fetch_address
from Utils.validations import hash_password


async def _handle_cep(entity: EmployeeModel, cep: str) -> None:
    address = await fetch_address(cep)
    address["complement"] = entity.address.get("complement")
    entity.address = address


def _handle_password(entity: EmployeeModel, password: str) -> None:
    entity.password_hash = hash_password(password)


class EmployeeService(BaseService[EmployeeModel, EmployeeSchema, EmployeeUpdateSchema]):
    def __init__(self, session: Session):
        super().__init__(session, EmployeeRepository, EmployeeModel, "Employee")
        self.audit_service = AuditService(session)

    async def create_employee(self, employee_data: EmployeeSchema) -> EmployeeModel:
        address = await fetch_address(employee_data.cep)
        address["complement"] = employee_data.complement

        employee = EmployeeModel(
            id=str(uuid7()),
            name=employee_data.name,
            email=employee_data.email,
            phone=employee_data.phone,
            password_hash=hash_password(employee_data.password),
            address=address,
            store_id=employee_data.store_id,
            role=employee_data.role
        )
        return self.create(employee)

    async def update_employee(self, employee_id: str, employee_data: EmployeeUpdateSchema) -> EmployeeModel:
        return await self.update_by_id(
            employee_id,
            employee_data,
            field_handlers={
                "password": _handle_password,
                "cep": _handle_cep,
            }
        )

    async def get_all_paginated(self, page: int, page_size: int) -> PaginatedEmployeeResponse:
        """Get paginated employees for all stores."""
        result = await self.get_paginated(page, page_size)

        return PaginatedEmployeeResponse(
            data=result["data"],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"]
        )

    async def get_all_by_store(self, store_id: str, page: int, page_size: int) -> PaginatedEmployeeResponse:
        """Get paginated employees for a specific store."""
        result = await self.get_paginated_by_store(store_id, page, page_size)

        return PaginatedEmployeeResponse(
            data=result["data"],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"]
        )
