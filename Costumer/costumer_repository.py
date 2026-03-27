from typing import Sequence
from sqlmodel import Session, select

from Costumer.costumer import CostumerModel


class CostumerRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, costumer: CostumerModel) -> CostumerModel:
        self.session.add(costumer)
        self.session.commit()
        self.session.refresh(costumer)
        return costumer

    def get_all(self) -> Sequence[CostumerModel]:
        return self.session.exec(select(CostumerModel)).all()

    def get_by_id(self, costumer_id: str) -> CostumerModel | None:
        return self.session.get(CostumerModel, costumer_id)

    def get_by_email(self, email: str) -> CostumerModel | None:
        return self.session.exec(select(CostumerModel).where(CostumerModel.email == email)).first()

    def delete(self, costumer_id: str) -> None:
        costumer = self.get_by_id(costumer_id)
        if costumer:
            self.session.delete(costumer)
            self.session.commit()
        else:
            raise ValueError(f"Costumer with id {costumer_id} not found")
