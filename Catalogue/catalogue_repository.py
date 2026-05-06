from typing import Sequence
from sqlmodel import Session, select

from Catalogue.catalogue import CatalogueModel
from Utils.base_repository import BaseRepository
from Inventory.inventory import InventoryModel
from Catalogue.dish_ingredient import DishIngredient


class CatalogueRepository(BaseRepository[CatalogueModel]):
    def __init__(self, session: Session):
        super().__init__(session, CatalogueModel)

    def get_by_name(self, name: str, store_id: str) -> CatalogueModel | None:
        """Busca um prato pelo nome e store_id."""
        statement = select(CatalogueModel).where(
            (CatalogueModel.name == name) & (CatalogueModel.store_id == store_id)
        )
        return self.session.exec(statement).first()

    def get_ingredients_for_dish(self, dish_id: str) -> Sequence[tuple[InventoryModel, DishIngredient]]:
        """Retorna lista de ingredientes e suas quantidades para um prato."""
        statement = (
            select(InventoryModel, DishIngredient)
            .join(DishIngredient)
            .where(DishIngredient.dish_id == dish_id)
        )
        results = self.session.exec(statement).all()
        return results
