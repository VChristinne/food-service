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

        for field in list(update_data.keys()):
            match field:
                case "name":
                    existing_employee.name = update_data["name"]
                case "password":
                    existing_employee.password_hash = hash_password(update_data["password"])
                case "email":
                    existing_employee.email = update_data["email"]
                case "phone":
                    existing_employee.phone = update_data["phone"]
                case "cep":
                    address = await fetch_address(update_data["cep"])
                    address["complement"] = update_data.get("complement", existing_employee.address.get("complement"))
                    existing_employee.address = address
                case "role":
                    existing_employee.role = update_data["role"]

        update_data["updated_at"] = int(time())
        existing_employee.updated_at = int(time())
        return self.repository.update(existing_employee)
