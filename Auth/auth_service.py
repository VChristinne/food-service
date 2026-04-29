from fastapi import HTTPException, status
from sqlmodel import Session

from Employee.employee_repository import EmployeeRepository
from Costumer.costumer_repository import CostumerRepository
from Auth.auth import create_access_token
from Utils.validations import verify_password


class AuthService:
    def __init__(self, session: Session):
        self.emploee_repository = EmployeeRepository(session)
        self.costumer_repository = CostumerRepository(session)

    async def login(self, email: str, password: str) -> dict:
        is_employee = email.endswith("@raizesnordeste.com")

        if is_employee:
            user = self.emploee_repository.get_by_email(email)
            if not user or not verify_password(password, user.password_hash):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email or password is invalid")
            role = user.role
            user_id = user.id
        else:
            user = self.costumer_repository.get_by_email(email)
            if not user or not verify_password(password, user.password_hash):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email or password is invalid")
            role = "COSTUMER"
            user_id = user.id

        token = create_access_token(data={
            "sub": user_id,
            "email": email,
            "role": role
        })

        return {
            "id": user_id,
            "access_token": token,
            "token_type": "Bearer"
        }

    async def logout(self) -> dict:
        return {"message": "Logout successful"}
