from fastapi import HTTPException, status, Request
from typing import Sequence
from sqlmodel import Session
from uuid_extensions import uuid7
from time import time

from Catalogue.catalogue import CatalogueSchema, CatalogueModel, CatalogueUpdateSchema
from Catalogue.catalogue_repository import CatalogueRepository
from Audit.audit_service import AuditService


class CatalogueService:
    def __init__(self, session: Session):
        self.repository = CatalogueRepository(session)
        self.audit_service = AuditService(session)

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

    async def update_dish(self, dish_id: str, dish_data: CatalogueUpdateSchema) -> CatalogueModel:
        existing_dish = self.repository.get_by_id(dish_id)
        if not existing_dish:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dish not found")

        update_data = dish_data.model_dump(exclude_unset=True)

        for field in list(update_data.keys()):
            match field:
                case "name":
                    existing_dish.name = update_data["name"]
                case "price":
                    existing_dish.price = update_data["price"]
                case "available":
                    existing_dish.available = update_data["available"]

        update_data["updated_at"] = int(time())
        return self.repository.update(existing_dish)

    async def delete_dish(self, dish_id: str, request: Request) -> None:
        existing_dish = self.repository.get_by_id(dish_id)
        if not existing_dish:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dish not found")
        self.repository.delete(dish_id)
