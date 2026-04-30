from fastapi import APIRouter, Depends, status, Request
from sqlmodel import Session
from pydantic import BaseModel

from Auth.auth import get_current_user
from main import save_log
from Database.db_config import db
from Audit.audit import AuditActionEnum
from Auth.auth_service import AuthService

router = APIRouter()


class LoginSchema(BaseModel):
    email: str
    password: str


class BootstrapAdminSchema(BaseModel):
    name: str
    email: str
    password: str
    phone: str
    cep: str
    complement: str = None


def get_auth_service(session: Session = Depends(db.get_session)) -> AuthService:
    return AuthService(session)


@router.post("/bootstrap-admin", status_code=status.HTTP_201_CREATED)
async def bootstrap_admin(
    request: Request,
    admin_data: BootstrapAdminSchema,
    service: AuthService = Depends(get_auth_service)
) -> dict:
    """
    Cria o primeiro admin do sistema.
    Só funciona se não houver nenhum admin criado ainda.
    """
    return await service.create_first_admin(admin_data)


@router.post("/login", status_code=status.HTTP_200_OK)
@save_log(AuditActionEnum.LOGIN, "auth")
async def login(
        request: Request,
        credentials: LoginSchema,
        service: AuthService = Depends(get_auth_service),
) -> dict:
    return await service.login(credentials.email, credentials.password)


@router.post("/logout", status_code=status.HTTP_200_OK)
@save_log(AuditActionEnum.LOGOUT, "auth")
async def logout(
        request: Request,
        current_user: dict = Depends(get_current_user),
        service: AuthService = Depends(get_auth_service)
) -> dict:
    return await service.logout()
