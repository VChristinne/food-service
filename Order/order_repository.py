from sqlmodel import Session

from Order.order import OrderModel
from Utils.base_repository import BaseRepository


class OrderRepository(BaseRepository[OrderModel]):
    def __init__(self, session: Session):
        super().__init__(session, OrderModel)
