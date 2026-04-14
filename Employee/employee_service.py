from sqlmodel import Session
from uuid_extensions import uuid7

from Employee.employee import EmployeeSchema, EmployeeModel, EmployeeUpdateSchema
from Employee.employee_repository import EmployeeRepository
from Utils.base_service import BaseService
from Audit.audit_service import AuditService
from Utils.address import fetch_address
from Utils.validations import hash_password


class EmployeeService(BaseService[EmployeeModel, EmployeeSchema, EmployeeUpdateSchema]):
    def __init__(self, session: Session):
        super().__init__(session, EmployeeRepository, EmployeeModel, "Employee")
        self.audit_service = AuditService(session)

    async def create_employee(self, employee_data: EmployeeSchema) -> EmployeeModel:
        """Cria employee com transformações (password hash, address fetch)"""
        address = await fetch_address(employee_data.cep)
        address["complement"] = employee_data.complement

        employee = EmployeeModel(
            id=str(uuid7()),
            name=employee_data.name,
            email=employee_data.email,
            phone=employee_data.phone,
            password_hash=hash_password(employee_data.password),
            address=address,
            role=employee_data.role
        )
        return self.create(employee)

    async def update_employee(self, employee_id: str, employee_data: EmployeeUpdateSchema) -> EmployeeModel:
        """Atualiza employee com handlers customizados"""
        return await self.update_by_id(
            employee_id,
            employee_data,
            field_handlers={
                "password": self._handle_password,
                "cep": self._handle_cep,
            }
        )

    def _handle_password(self, entity: EmployeeModel, password: str) -> None:
        """Atualiza password com hash"""
        entity.password_hash = hash_password(password)

    async def _handle_cep(self, entity: EmployeeModel, cep: str) -> None:
        """Atualiza endereço a partir do CEP"""
        address = await fetch_address(cep)
        address["complement"] = entity.address.get("complement")
        entity.address = address
