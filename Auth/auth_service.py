from sqlmodel import Session

from Costumer.costumer_repository import CostumerRepository
from Auth.auth import create_access_token
from Utils.validations import verify_password


class AuthService:
    def __init__(self, session: Session):
        self.costumer_repository = CostumerRepository(session)

    async def login(self, email: str, password: str) -> dict:
        costumer = self.costumer_repository.get_by_email(email)

        if not costumer or not verify_password(password, costumer.password_hash):
            raise ValueError("Email or password is invalid")

        token = create_access_token(data={
            "sub": costumer.id,
            "email": costumer.email
        })

        return {
            "id": costumer.id,
            "access_token": token,
            "token_type": "bearer"
        }