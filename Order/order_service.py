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
        StatusEnum.PENDING: [StatusEnum.PREPARING, StatusEnum.CANCELED],
        StatusEnum.PREPARING: [StatusEnum.TRANSIT, StatusEnum.CANCELED],
        StatusEnum.TRANSIT: [StatusEnum.DELIVERED, StatusEnum.FAILED],
        StatusEnum.DELIVERED: [],
        StatusEnum.FAILED: [],
        StatusEnum.CANCELED: [],
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

    async def cancel_order(self, order_id: str, store_id: str) -> OrderModel:
        order = await self.get_by_id_and_store(order_id, store_id)

        if order.status not in [StatusEnum.PENDING, StatusEnum.PREPARING]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Pedido com status '{order.status.value}' não pode ser cancelado. "
                       f"Cancelamento permitido apenas em 'pendente' ou 'preparando'."
            )

        order.status = StatusEnum.CANCELED
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
        return self.repository.create(new_order)
