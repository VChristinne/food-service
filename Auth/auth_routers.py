from sqlmodel import Session
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from Database.db_config import db
from Auth.auth_service import AuthService
from Auth.auth import get_current_user

router = APIRouter()


class LoginSchema(BaseModel):
    email: str
    password: str


def get_auth_service(session: Session = Depends(db.get_session)) -> AuthService:
    return AuthService(session)


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
        credentials: LoginSchema,
        service: AuthService = Depends(get_auth_service),
        current_user: dict = Depends(get_current_user)
) -> dict:
    return await service.login(credentials.email, credentials.password, current_user["sub"])  # noqa
