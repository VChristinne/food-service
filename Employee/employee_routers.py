from fastapi import APIRouter, Depends, status, Request, Query
from typing import Sequence
from sqlmodel import Session

from Employee.employee import EmployeeSchema, EmployeeModel, EmployeeUpdateSchema, PaginatedEmployeeResponse
from Employee.employee_service import EmployeeService
from Utils.ownership_decorator import require_roles
from main import save_log
from Database.db_config import db
from Audit.audit import AuditActionEnum
from Auth.auth import get_current_user

router = APIRouter()

def get_employee_service(session: Session = Depends(db.get_session)) -> EmployeeService:
    return EmployeeService(session)


@router.get("/", status_code=status.HTTP_200_OK, response_model=PaginatedEmployeeResponse)
@require_roles(["admin", "manager"])
@save_log(AuditActionEnum.READ, EmployeeModel)
async def get_employees(
    request: Request,
    page: int = Query(1, ge=1, description="Current page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    current_user: dict = Depends(get_current_user),
    service: EmployeeService = Depends(get_employee_service)
) -> PaginatedEmployeeResponse:
    return service.get_paginated_employees(page, page_size)

@router.get("/{employee_id}", status_code=status.HTTP_200_OK)
@require_roles(["admin", "manager"])
@save_log(AuditActionEnum.READ, EmployeeModel)
async def get_employee(
    request: Request,
    employee_id: str,
    current_user: dict = Depends(get_current_user),
    service: EmployeeService = Depends(get_employee_service)
) -> EmployeeModel:
    return await service.get_by_id(employee_id)

@router.post("/", status_code=status.HTTP_201_CREATED)
@require_roles(["admin", "manager"])
@save_log(AuditActionEnum.CREATE, EmployeeModel)
async def create_employee(
    request: Request,
    employee_data: EmployeeSchema,
    current_user: dict = Depends(get_current_user),
    service: EmployeeService = Depends(get_employee_service)
) -> EmployeeModel:
    new_employee = await service.create_employee(employee_data)
    return new_employee

@router.patch("/{employee_id}", status_code=status.HTTP_200_OK)
@require_roles(["admin", "manager"])
@save_log(AuditActionEnum.UPDATE, EmployeeModel)
async def update_employee(
    request: Request,
    employee_id: str,
    employee_data: EmployeeUpdateSchema,
    current_user: dict = Depends(get_current_user),
    service: EmployeeService = Depends(get_employee_service)
) -> EmployeeModel:
    updated_employee = await service.update_by_id(employee_id, employee_data)
    return updated_employee

# TODO: IMPLEMENT SOFT DELETE
