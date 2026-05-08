from sqlmodel import Session, select, func

from Customer.customer import CustomerModel
from Utils.base_repository import BaseRepository


class CustomerRepository(BaseRepository[CustomerModel]):
    def __init__(self, session: Session):
        super().__init__(session, CustomerModel)

    def get_by_email(self, email: str) -> CustomerModel | None:
        normalized_email = email.strip().lower()
        return self.session.exec(
            select(CustomerModel).where(func.lower(CustomerModel.email) == normalized_email)
        ).first()
