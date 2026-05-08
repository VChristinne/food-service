from fastapi import APIRouter, Depends, status, Request, Query
from typing import Sequence
from sqlmodel import Session

from Customer.customer import CustomerSchema, CustomerModel, CustomerUpdateSchema, PaginatedCustomerResponse
from Customer.customer_service import CustomerService
from Utils.ownership_decorator import require_roles
from main import save_log
from Database.db_config import db
from Audit.audit import AuditActionEnum
from Auth.auth import get_current_user

router = APIRouter()

def get_customer_service(session: Session = Depends(db.get_session)) -> CustomerService:
    return CustomerService(session)


@router.get("/", status_code=status.HTTP_200_OK, response_model=PaginatedCustomerResponse)
@require_roles(["admin"])
@save_log(AuditActionEnum.READ, CustomerModel)
async def get_customers(
        request: Request,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(10, ge=1, description="Number of items per page"),
        current_user: dict = Depends(get_current_user),
        service: CustomerService = Depends(get_customer_service)
) -> PaginatedCustomerResponse:
    return await service.get_all_paginated(page, page_size)

@router.get("/{customer_id}", status_code=status.HTTP_200_OK)
@require_roles(["admin"])
@save_log(AuditActionEnum.READ, CustomerModel)
async def get_customer(
        request: Request,
        customer_id: str,
        current_user: dict = Depends(get_current_user),
        service: CustomerService = Depends(get_customer_service)
) -> CustomerModel:
    return await service.get_by_id(customer_id)

@router.post("/", status_code=status.HTTP_201_CREATED)
@save_log(AuditActionEnum.CREATE, CustomerModel)
async def create_customer(
        request: Request,
        customer_data: CustomerSchema,
        service: CustomerService = Depends(get_customer_service)
) -> CustomerModel:
    new_customer = await service.create_customer(customer_data)
    return new_customer

@router.patch("/{customer_id}", status_code=status.HTTP_200_OK)
@require_roles(["owner"])
@save_log(AuditActionEnum.UPDATE, CustomerModel)
async def update_customer(
        request: Request,
        customer_id: str,
        customer_data: CustomerUpdateSchema,
        current_user: dict = Depends(get_current_user),
        service: CustomerService = Depends(get_customer_service)
) -> CustomerModel:
    updated_customer = await service.update_customer(customer_id, customer_data)
    return updated_customer
