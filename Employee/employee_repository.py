from typing import Any

from sqlalchemy import Row
from sqlmodel import Session, select, func

from Employee.employee import EmployeeModel
from Utils.base_repository import BaseRepository


class EmployeeRepository(BaseRepository[EmployeeModel]):
    def __init__(self, session: Session):
        super().__init__(session, EmployeeModel)

    def get_by_email(self, email: str) -> Row[Any] | None | Any:
        return self.session.exec(
            select(EmployeeModel).where(func.lower(EmployeeModel.email) == email.lower())
        ).first()
