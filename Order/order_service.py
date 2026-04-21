from fastapi import HTTPException, status
from sqlmodel import Session
from uuid_extensions import uuid7
from decimal import Decimal

from Order.order import OrderModel, OrderSchema, OrderUpdateSchema
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


class OrderService(BaseService[OrderModel, OrderSchema, OrderUpdateSchema]):
    def __init__(self, session: Session):
        super().__init__(session, OrderRepository, OrderModel, "Order")
        self.audit_service = AuditService(session)
        self.catalogue_service = CatalogueService(session)
        self.inventory_service = InventoryService(session)
        self.costumer_service = CostumerService(session)

    async def create_order(self, order_data: OrderSchema, costumer_id: str) -> OrderModel:
        """Cria um novo pedido com validação, cálculo de preço e dedução de estoque."""
        validated_items, subtotal = await self._validate_and_process_items(order_data.items)
        final_price, points_earned = _calculate_totals(subtotal)

        order = OrderModel(
            id=str(uuid7()),
            costumer_id=costumer_id,
            channel=order_data.channel,
            type=order_data.type,
            items=validated_items,
            notes=order_data.notes,
            payment_method=order_data.payment_method,
            price=final_price,
            pointsEarned=points_earned,
            table_number=order_data.table_number,
            delivery_address=order_data.delivery_address,
            status=order_data.status
        )

        await self._decrease_inventory(validated_items)
        created_order = self.create(order)

        await self._update_costumer_loyalty(costumer_id, created_order.id, points_earned)
        return created_order

    async def _update_costumer_loyalty(self, costumer_id: str, order_id: str, points: int) -> None:
        costumer = await self.costumer_service.get_by_id(costumer_id)
        costumer.points += points
        costumer.orders = (costumer.orders or []) + [order_id]
        self.costumer_service.update(costumer)

    async def _validate_and_process_items(self, items: list[dict]) -> tuple[list[dict], Decimal]:
        validated_items = []
        subtotal = Decimal("0")

        for item in items:
            dish = await self.catalogue_service.get_by_id(item["dish_id"])

            if not dish.available:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Prato '{dish.name}' não está disponível"
                )

            quantity = Decimal(str(item["quantity"]))
            item_total = dish.price * quantity
            subtotal += item_total

            validated_items.append({
                "dish_id": item["dish_id"],
                "quantity": int(quantity)
            })

        return validated_items, subtotal

    async def _decrease_inventory(self, validated_items: list[dict]) -> None:
        for item in validated_items:
            dish = await self.catalogue_service.get_by_id(item["dish_id"])
            for ingredient in dish.ingredients:
                await self.decrease(ingredient.id, ingredient.quantity * item["quantity"])

    async def decrease(self, ingredient_id: str, quantity: Decimal) -> None:
        ingredient = await self.inventory_service.get_by_id(ingredient_id)

        if ingredient.quantity < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estoque insuficiente para {ingredient.name}"
            )

        ingredient.quantity -= quantity
        self.inventory_service.update(ingredient)

    async def increase(self, ingredient_id: str, quantity: Decimal) -> None:
        ingredient = await self.inventory_service.get_by_id(ingredient_id)
        ingredient.quantity += quantity
        self.inventory_service.update(ingredient)

    async def reserve(self, ingredient_id: str, quantity: Decimal) -> None:
        ingredient = await self.inventory_service.get_by_id(ingredient_id)

        if ingredient.quantity < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estoque insuficiente para {ingredient.name}"
            )
