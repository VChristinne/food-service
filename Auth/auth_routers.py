from fastapi import APIRouter, Depends, status, Request
from sqlmodel import Session
from pydantic import BaseModel

from main import save_log
from Database.db_config import db
from Audit.audit import AuditActionEnum
from Auth.auth_service import AuthService

router = APIRouter()


class LoginSchema(BaseModel):
    email: str
    password: str


def get_auth_service(session: Session = Depends(db.get_session)) -> AuthService:
    return AuthService(session)


@router.post("/login", status_code=status.HTTP_200_OK)
@save_log(AuditActionEnum.LOGIN, "auth")
async def login(
        request: Request,
        credentials: LoginSchema,
        service: AuthService = Depends(get_auth_service),
) -> dict:
    return await service.login(credentials.email, credentials.password)
