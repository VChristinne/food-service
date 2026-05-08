from fastapi import HTTPException, status
from sqlmodel import Session
from time import time
from decimal import Decimal

from Catalogue.catalogue import CatalogueModel, CatalogueSchema, CatalogueUpdateSchema, PaginatedCatalogueResponse
from Catalogue.dish_ingredient import DishIngredient
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
        dish = self.create_from_schema(schema, field_transformers=field_transformers)

        # Criar associações de ingredientes se foram fornecidos
        if schema.items:
            self._create_dish_ingredients(dish.id, schema.items)

        return dish

    def _create_dish_ingredients(self, dish_id: str, items: list[dict]) -> None:
        """Cria as associações entre prato e ingredientes."""
        for item in items:
            ingredient_id = item.get("ingredient_id")
            quantity = Decimal(str(item.get("quantity", 0)))

            dish_ingredient = DishIngredient(
                dish_id=dish_id,
                ingredient_id=ingredient_id,
                quantity=quantity
            )
            self.repository.session.add(dish_ingredient)

        self.repository.session.commit()

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

    async def get_all_paginated(self, page: int, page_size: int) -> PaginatedCatalogueResponse:
        """Get paginated dishes for all stores."""
        result = await self.get_paginated(page, page_size)

        return PaginatedCatalogueResponse(
            data=result["data"],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"]
        )

    async def get_all_by_store(self, store_id: str, page: int, page_size: int) -> PaginatedCatalogueResponse:
        """Get paginated dishes for a specific store."""
        result = await self.get_paginated_by_store(store_id, page, page_size)

        return PaginatedCatalogueResponse(
            data=result["data"],
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"]
        )
