from fastapi import APIRouter, Depends, status, Request
from typing import Sequence
from sqlmodel import Session

from Order.order import OrderModel, OrderSchema
from Order.order_service import OrderService
from Utils.ownership_decorator import require_roles
from Auth.auth import get_current_user
from main import save_log
from Database.db_config import db
from Audit.audit import AuditActionEnum

router = APIRouter()

def get_order_service(session: Session = Depends(db.get_session)) -> OrderService:
    return OrderService(session)


@router.get("/", status_code=status.HTTP_200_OK)
@require_roles(["manager", "waiter", "delivery"])
@save_log(AuditActionEnum.READ, OrderModel)
async def get_orders(
    request: Request,
    current_user: dict = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
) -> Sequence[OrderModel]:
    store_id = request.state.store_id
    return await service.get_all_by_store(store_id)

@router.get("/{order_id}", status_code=status.HTTP_200_OK)
@require_roles(["manager", "waiter", "delivery", "owner"])
@save_log(AuditActionEnum.READ, OrderModel)
async def get_order(
    request: Request,
    order_id: str,
    current_user: dict = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
) -> OrderModel:
    store_id = request.state.store_id
    return await service.get_by_id_and_store(order_id, store_id)

@router.get("/me/{costumer_id}", status_code=status.HTTP_200_OK)
@require_roles(["owner"])
@save_log(AuditActionEnum.READ, OrderModel)
async def get_my_orders(
    request: Request,
    costumer_id: str,
    current_user: dict = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
) -> Sequence[OrderModel]:
    return await service.get_by_costumer(costumer_id)

@router.post("/{store_id}/{costumer_id}", status_code=status.HTTP_201_CREATED)
@require_roles(["owner"])
@save_log(AuditActionEnum.CREATE, OrderModel)
async def create_order(
    request: Request,
    store_id: str,
    costumer_id: str,
    order_data: OrderSchema,
    current_user: dict = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
) -> OrderModel:
    return await service.create_for_costumer(costumer_id, store_id, order_data)
