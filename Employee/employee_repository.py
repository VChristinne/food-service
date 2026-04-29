from sqlmodel import Session, select, func

from Employee.employee import EmployeeModel
from Utils.base_repository import BaseRepository


class EmployeeRepository(BaseRepository[EmployeeModel]):
    def __init__(self, session: Session):
        super().__init__(session, EmployeeModel)

    def get_by_email(self, email: str) -> EmployeeModel | None:
        return self.session.exec(select(EmployeeModel).where(EmployeeModel.email == email)).first()

    def get_paginated(self, page: int, page_size: int) -> tuple[list[EmployeeModel], int]:
        offset = (page - 1) * page_size

        total = self.session.exec(select(func.count(EmployeeModel.id))).one()

        employees = self.session.exec(
            select(EmployeeModel)
            .offset(offset)
            .limit(page_size)
        ).all()

        return list(employees), total
