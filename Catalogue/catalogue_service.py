from fastapi import HTTPException, status
from sqlmodel import Session
from time import time

from Catalogue.catalogue import CatalogueModel, CatalogueSchema, CatalogueUpdateSchema
from Catalogue.catalogue_repository import CatalogueRepository
from Utils.base_service import BaseService
from Audit.audit_service import AuditService


class CatalogueService(BaseService[CatalogueModel, CatalogueSchema, CatalogueUpdateSchema]):
    def __init__(self, session: Session):
        super().__init__(session, CatalogueRepository, CatalogueModel, "Dish")
        self.audit_service = AuditService(session)

    async def validate_store_access(self, dish_id: str, store_id: str) -> CatalogueModel:
        dish = await self.get_by_id(dish_id)
        if dish.store_id != store_id:
            raise HTTPException(403, "Você não pode acessar pratos de outra loja")
        return dish

    def create_for_store(self, schema: CatalogueSchema, store_id: str) -> CatalogueModel:
        field_transformers = {
            "store_id": lambda _: store_id
        }
        return self.create_from_schema(schema, field_transformers=field_transformers)


    async def get_by_id_and_store(self, dish_id: str, store_id: str) -> CatalogueModel:
        dish = self.repository.get_by_id(dish_id)
        if not dish:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Prato não encontrado"
            )

        if dish.store_id != store_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não pode acessar pratos de outra loja"
            )

        return dish

    async def update_by_id(self, dish_id: str, schema: CatalogueUpdateSchema, store_id: str) -> CatalogueModel:
        dish = await self.get_by_id_and_store(dish_id, store_id)
        update_data = schema.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field in ["price", "name", "available"]:
                setattr(dish, field, value)

        dish.updated_at = int(time())
        return self.repository.update(dish)

    async def delete_by_store(self, dish_id: str, store_id: str) -> None:
        await self.get_by_id_and_store(dish_id, store_id)
        self.repository.delete(dish_id)

    async def mark_unavailable_if_out_of_stock(self, dish_id: str, store_id: str) -> CatalogueModel:
        dish = await self.get_by_id_and_store(dish_id, store_id)
        ingredients = self.repository.get_ingredients_for_dish(dish_id)

        for ingredient in ingredients:
            if ingredient.quantity <= ingredient.min_quantity:
                dish.available = False
                return self.repository.update(dish)
        return dish
