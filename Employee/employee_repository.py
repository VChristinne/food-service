from sqlmodel import Session, select

from Employee.employee import EmployeeModel
from Utils.base_repository import BaseRepository


class EmployeeRepository(BaseRepository[EmployeeModel]):
    def __init__(self, session: Session):
        super().__init__(session, EmployeeModel)

    def get_by_email(self, email: str) -> EmployeeModel | None:
        return self.session.exec(select(EmployeeModel).where(EmployeeModel.email == email)).first()

