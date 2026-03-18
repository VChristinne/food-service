from typing import Sequence
from sqlmodel import Session, select

from Catalogue.catalogue import CatalogueModel


class CatalogueRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, client: CatalogueModel) -> CatalogueModel:
        self.session.add(client)
        self.session.commit()
        self.session.refresh(client)
        return client

    def get_all(self) -> Sequence[CatalogueModel]:
        return self.session.exec(select(CatalogueModel)).all()

    def get_by_id(self, dish_id: str) -> CatalogueModel | None:
        return self.session.get(CatalogueModel, dish_id)
