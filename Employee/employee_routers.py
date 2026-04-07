from fastapi import APIRouter, Depends, status, Request, HTTPException
from typing import Sequence

from sqlalchemy.sql.functions import current_user
from sqlmodel import Session

from Employee.employee import EmployeeSchema, EmployeeModel, EmployeeUpdateSchema, RoleEnum
from Employee.employee_service import EmployeeService
from main import audit_decorator
from Database.db_config import db
from Audit.audit import AuditActionEnum
from Auth.auth import get_current_user

router = APIRouter()


def get_employee_service(session: Session = Depends(db.get_session)) -> EmployeeService:
    return EmployeeService(session)


@router.get("/", status_code=status.HTTP_200_OK)
@audit_decorator.log(AuditActionEnum.READ, EmployeeModel)
async def get_employees(
        request: Request,
        current_user: EmployeeService = Depends(get_current_user),
        service: EmployeeService = Depends(get_employee_service)
) -> Sequence[EmployeeModel]:
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Acesso negado")
    return await service.get_employees()


@router.post("/", status_code=status.HTTP_201_CREATED)
@audit_decorator.log(AuditActionEnum.CREATE, EmployeeModel)
async def create_admin_employee(
        request: Request,
        employee_data: EmployeeSchema,
        service: EmployeeService = Depends(get_employee_service),
) -> EmployeeModel:
    employee = await service.create_employee(employee_data)
    return employee


@router.post("/", status_code=status.HTTP_201_CREATED)
@audit_decorator.log(AuditActionEnum.CREATE, EmployeeModel)
async def create_employee(
        request: Request,
        employee_data: EmployeeSchema,
        service: EmployeeService = Depends(get_employee_service),
) -> EmployeeModel:
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Acesso negado")
    employee = await service.create_employee(employee_data)
    return employee


@router.patch("/{employee_id}", status_code=status.HTTP_200_OK)
@audit_decorator.log(AuditActionEnum.UPDATE, EmployeeModel)
async def update_employee(
        request: Request,
        employee_id: str,
        employee_data: EmployeeUpdateSchema,
        service: EmployeeService = Depends(get_employee_service),
) -> EmployeeModel:
    updated_employee = await service.update_employee(employee_id, employee_data)
    return updated_employee
