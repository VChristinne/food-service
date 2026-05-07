from fastapi import HTTPException, status
from sqlmodel import Session
from time import time
from decimal import Decimal

from Inventory.inventory import InventoryModel, InventorySchema, InventoryUpdateSchema
from Inventory.inventory_repository import InventoryRepository
from Utils.base_service import BaseService
from Audit.audit_service import AuditService


class InventoryService(BaseService[InventoryModel, InventorySchema, InventoryUpdateSchema]):
    def __init__(self, session: Session):
        super().__init__(session, InventoryRepository, InventoryModel, "Inventory")
        self.audit_service = AuditService(session)

    async def validate_store_access(self, inventory_id: str, store_id: str) -> InventoryModel:
        inventory = await self.get_by_id(inventory_id)
        if inventory.store_id != store_id:
            raise HTTPException(403, "Você não pode acessar inventário de outra loja")
        return inventory

    def create_for_store(self, schema: InventorySchema, store_id: str) -> InventoryModel:
        field_transformers = {
            "store_id": lambda _: store_id
        }
        return self.create_from_schema(schema, field_transformers=field_transformers)

    async def get_by_id_and_store(self, inventory_id: str, store_id: str) -> InventoryModel:
        inventory = self.repository.get_by_id(inventory_id)
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item de inventário não encontrado"
            )

        if inventory.store_id != store_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não pode acessar itens de inventário de outra loja"
            )

        return inventory

    async def update_by_id(self, inventory_id: str, schema: InventoryUpdateSchema, store_id: str) -> InventoryModel:
        inventory = await self.get_by_id_and_store(inventory_id, store_id)
        update_data = schema.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field in ["name", "quantity"]:
                setattr(inventory, field, value)

        inventory.updated_at = int(time())
        return self.repository.update(inventory)

    async def delete_by_store(self, inventory_id: str, store_id: str) -> None:
        await self.get_by_id_and_store(inventory_id, store_id)
        self.repository.delete(inventory_id)

    async def reduce_quantity(self, inventory_id: str, quantity: Decimal) -> InventoryModel:
        """Reduz a quantidade de um item de inventário."""
        inventory = self.repository.get_by_id(inventory_id)
        if not inventory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item de inventário não encontrado"
            )

        if inventory.quantity < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Quantidade insuficiente em estoque. Disponível: {inventory.quantity}, Solicitado: {quantity}"
            )

        inventory.quantity -= quantity
        inventory.updated_at = int(time())
        return self.repository.update(inventory)
