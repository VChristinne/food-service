from fastapi import HTTPException, status
from sqlmodel import Session
from uuid_extensions import uuid7
from decimal import Decimal
from time import time
from typing import Sequence

from Order.order import OrderModel, OrderSchema, OrderUpdateSchema, StatusEnum
from Order.order_repository import OrderRepository
from Catalogue.catalogue_service import CatalogueService
from Inventory.inventory_service import InventoryService
from Costumer.costumer_service import CostumerService
from Utils.base_service import BaseService
from Audit.audit_service import AuditService

FOOD_TAX_RATE = Decimal("0.10")
POINTS_MULTIPLIER = Decimal("1")


def _calculate_totals(subtotal: Decimal) -> tuple[Decimal, int]:
    tax = subtotal * FOOD_TAX_RATE
    final_price = subtotal + tax
    points_earned = int(final_price * POINTS_MULTIPLIER)
    return final_price, points_earned


def _validate_status_transition(current: StatusEnum, new: StatusEnum) -> None:
    valid_transitions = {
        StatusEnum.PENDING: [StatusEnum.PREPARING, StatusEnum.FAILED],
        StatusEnum.PREPARING: [StatusEnum.TRANSIT, StatusEnum.FAILED],
        StatusEnum.TRANSIT: [StatusEnum.DELIVERED, StatusEnum.FAILED],
        StatusEnum.DELIVERED: [],
        StatusEnum.FAILED: [],
    }

    if new not in valid_transitions.get(current, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transição inválida: '{current.value}' → '{new.value}'"
        )


class OrderService(BaseService[OrderModel, OrderSchema, OrderUpdateSchema]):
    def __init__(self, session: Session):
        super().__init__(session, OrderRepository, OrderModel, "Order")
        self.audit_service = AuditService(session)
        self.catalogue_service = CatalogueService(session)
        self.inventory_service = InventoryService(session)
        self.costumer_service = CostumerService(session)

    async def get_by_costumer(self, costumer_id: str) -> Sequence[OrderModel]:
        return self.repository.get_all_by_costumer(costumer_id)

    async def get_by_id_and_store(self, order_id: str, store_id: str) -> OrderModel:
        order = self.repository.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido não encontrado"
            )

        if order.store_id != store_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não pode acessar pedidos de outra loja"
            )

        return order

    async def update_order_status(self, order_id: str, new_status: StatusEnum, store_id: str) -> OrderModel:
        order = await self.get_by_id_and_store(order_id, store_id)
        _validate_status_transition(order.status, new_status)
        order.status = new_status
        order.updated_at = int(time())
        return self.repository.update(order)

    async def create_for_costumer(self, costumer_id: str, store_id: str, order_data: OrderSchema) -> OrderModel:
        costumer = await self.costumer_service.get_by_id(costumer_id)
        if not costumer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )

        subtotal = Decimal("0.00")

        for item in order_data.items:
            dish_name = item.get("name")
            item_quantity = Decimal(str(item.get("quantity", 1)))

            # Buscar prato pelo nome
            dish = self.catalogue_service.repository.get_by_name(dish_name, store_id)
            if not dish:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Prato '{dish_name}' não encontrado no catálogo"
                )

            subtotal += dish.price * item_quantity

        total_price, points_earned = _calculate_totals(subtotal)

        order_id = str(uuid7())
        new_order = OrderModel(
            id=order_id,
            costumer_id=costumer_id,
            store_id=store_id,
            channel=order_data.channel,
            type=order_data.type,
            items=order_data.items,
            notes=order_data.notes,
            payment_method=order_data.payment_method,
            price=total_price,
            pointsEarned=points_earned,
            table_number=order_data.table_number,
            delivery_address=order_data.delivery_address,
            status=StatusEnum.PENDING
        )

        # Reduzir inventário para cada item do pedido
        for item in order_data.items:
            dish_name = item.get("name")
            item_quantity = Decimal(str(item.get("quantity", 1)))

            # Buscar prato pelo nome
            dish = self.catalogue_service.repository.get_by_name(dish_name, store_id)
            if not dish:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Prato '{dish_name}' não encontrado no catálogo"
                )

            # Obter ingredientes do prato com suas quantidades
            ingredients = self.catalogue_service.repository.get_ingredients_for_dish(dish.id)

            # Reduzir quantidade de cada ingrediente
            for ingredient, dish_ingredient in ingredients:
                quantity_to_reduce = dish_ingredient.quantity * item_quantity
                self.inventory_service.reduce_quantity(ingredient.id, quantity_to_reduce)

        return self.repository.create(new_order)
