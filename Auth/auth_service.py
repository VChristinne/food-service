from sqlmodel import Session

from Client.client_repository import ClientRepository
from Auth.auth import create_access_token
from Utils.validations import verify_password


class AuthService:
    def __init__(self, session: Session):
        self.client_repository = ClientRepository(session)

    async def login(self, email: str, password: str) -> dict:
        client = self.client_repository.get_by_email(email)

        if not client or not verify_password(password, client.password_hash):
            raise ValueError("Email or password is invalid")

        token = create_access_token(data={
            "sub": client.id,
            "email": client.email
        })

        return {
            "access_token": token,
            "token_type": "bearer",
            "name": client.name
        }