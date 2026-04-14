from sqlmodel import Session, select

from Costumer.costumer import CostumerModel
from Utils.base_repository import BaseRepository


class CostumerRepository(BaseRepository[CostumerModel]):
    def __init__(self, session: Session):
        super().__init__(session, CostumerModel)

    def get_by_email(self, email: str) -> CostumerModel | None:
        return self.session.exec(select(CostumerModel).where(CostumerModel.email == email)).first()

