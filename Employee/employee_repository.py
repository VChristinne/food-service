from sqlmodel import Session, select
from typing import Sequence
from time import time

from Employee.employee import EmployeeModel


class EmployeeRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, employee: EmployeeModel) -> EmployeeModel:
        self.session.add(employee)
        self.session.commit()
        self.session.refresh(employee)
        return employee

    def update(self, employee: EmployeeModel) -> EmployeeModel:
        existing = self.get_by_id(employee.id)
        if not existing:
            raise ValueError(f"Employee with id {employee.id} not found")
        self.session.add(employee)
        self.session.commit()
        self.session.refresh(employee)
        return employee

    def get_all(self) -> Sequence[EmployeeModel]:
        return self.session.exec(select(EmployeeModel)).all()

    def get_by_id(self, employee_id: str) -> EmployeeModel | None:
        return self.session.get(EmployeeModel, employee_id)

    def get_by_email(self, email: str) -> EmployeeModel | None:
        return self.session.exec(select(EmployeeModel).where(EmployeeModel.email == email)).first()

    def delete(self, employee_id: str) -> None:
        employee = self.get_by_id(employee_id)
        if employee:
            self.session.delete(employee)
            self.session.commit()
        else:
            raise ValueError(f"Employee with id {employee_id} not found")
