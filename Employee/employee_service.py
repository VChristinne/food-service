from fastapi import HTTPException, status
from typing import Sequence
from sqlmodel import Session
from uuid_extensions import uuid7
from time import time

from Employee.employee import EmployeeSchema, EmployeeModel, EmployeeUpdateSchema
from Employee.employee_repository import EmployeeRepository
from Audit.audit_service import AuditService
from Utils.address import fetch_address
from Utils.validations import hash_password


class EmployeeService:
    def __init__(self, session: Session):
        self.repository = EmployeeRepository(session)
        self.audit_service = AuditService(session)

    async def get_employees(self) -> Sequence[EmployeeModel]:
        return self.repository.get_all()

    async def create_employee(self, employee_data: EmployeeSchema) -> EmployeeModel:
        address = await fetch_address(employee_data.cep)
        address["complement"] = employee_data.complement

        employee = EmployeeModel(
            id=str(uuid7()),
            name=employee_data.name,
            password_hash=hash_password(employee_data.password),
            email=employee_data.email,
            phone=employee_data.phone,
            address=address,
            role=employee_data.role
        )
        return self.repository.create(employee)

    async def update_employee(self, employee_id: str, employee_data: EmployeeUpdateSchema) -> EmployeeModel:
        existing_employee = self.repository.get_by_id(employee_id)
        if not existing_employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

        update_data = employee_data.model_dump(exclude_unset=True)
        for field, value in list(update_data.items()):
            match field:
                case "password":
                    update_data["password"] = hash_password(update_data.pop("password"))
                case "email":
                    update_data["email"] = update_data.pop("email")
                case "phone":
                    update_data["phone"] = update_data.pop("phone")
                case "cep":
                    update_data["cep"] = update_data.pop("cep")
                case "complement":
                    update_data["complement"] = update_data.pop("complement")
                case "role":
                    update_data["role"] = update_data.pop("role")

        update_data["updated_at"] = int(time())
        existing_employee.updated_at = int(time())
        return self.repository.update(existing_employee)
