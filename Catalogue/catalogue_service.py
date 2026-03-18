from typing import Sequence
from uuid import uuid7
from sqlmodel import Session

from Catalogue.catalogue import CatalogueSchema, CatalogueModel
from Catalogue.catalogue_repository import CatalogueRepository


class CatalogueService:
    def __init__(self, session: Session):
        self.repository = CatalogueRepository(session)

    async def get_catalogue(self) -> Sequence[CatalogueModel]:
        return self.repository.get_all()

    async def create_dish(self, catalogue_data: CatalogueSchema) -> CatalogueModel:
        dish = CatalogueModel(
            id=str(uuid7()),
            name=catalogue_data.name,
            price=catalogue_data.price,
            available=catalogue_data.available
        )
        return self.repository.create(dish)

    async def update_dish(self, dish_id, update_data):
        pass

    async def delete_dish(self, dish_id):
        pass