from sqlmodel import Session, select

from Order.order import OrderModel
from Utils.base_repository import BaseRepository


class OrderRepository(BaseRepository[OrderModel]):
    def __init__(self, session: Session):
        super().__init__(session, OrderModel)

    def get_all_by_customer(self, customer_id: str):
        statement = select(OrderModel).where(OrderModel.customer_id == customer_id)
        return self.session.exec(statement).all()
