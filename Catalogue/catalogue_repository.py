from typing import Sequence
from sqlmodel import Session, select

from Catalogue.catalogue import CatalogueModel


class CatalogueRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, catalogue: CatalogueModel) -> CatalogueModel:
        self.session.add(catalogue)
        self.session.commit()
        self.session.refresh(catalogue)
        return catalogue

    def update(self, catalogue: CatalogueModel) -> CatalogueModel:
        existing = self.get_by_id(catalogue.id)
        if not existing:
            raise ValueError(f"Catalogue with id {catalogue.id} not found")
        self.session.add(catalogue)
        self.session.commit()
        self.session.refresh(catalogue)
        return catalogue

    def get_all(self) -> Sequence[CatalogueModel]:
        return self.session.exec(select(CatalogueModel)).all()

    def get_by_id(self, dish_id: str) -> CatalogueModel | None:
        return self.session.get(CatalogueModel, dish_id)

    def delete(self, dish_id: str) -> None:
        dish = self.get_by_id(dish_id)
        if dish:
            self.session.delete(dish)
            self.session.commit()
        else:
            raise ValueError(f"Dish with id {dish_id} not found")
