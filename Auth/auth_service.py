from fastapi import HTTPException, status
from sqlmodel import Session
from uuid_extensions import uuid7

from Employee.employee_repository import EmployeeRepository
from Employee.employee import EmployeeModel, RoleEnum
from Costumer.costumer_repository import CostumerRepository
from Auth.auth import create_access_token
from Utils.validations import verify_password, hash_password
from Utils.address import fetch_address


class AuthService:
    def __init__(self, session: Session):
        self.emploee_repository = EmployeeRepository(session)
        self.costumer_repository = CostumerRepository(session)

    async def create_first_admin(self, admin_data) -> dict:
        """
        Cria o primeiro admin do sistema.
        Só funciona se não houver nenhum employee com role 'admin' criado ainda.
        """
        # Verifica se já existe admin
        all_employees = self.emploee_repository.get_all()
        admin_exists = any(emp.role == RoleEnum.ADMIN for emp in all_employees)

        if admin_exists:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin já existe no sistema. Entre em contato com o administrador."
            )

        normalized_email = admin_data.email.strip().lower()
        if not normalized_email.endswith("@raizesnordeste.com"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email deve ser do domínio @raizesnordeste.com"
            )

        address = await fetch_address(admin_data.cep)
        address["complement"] = admin_data.complement

        admin = EmployeeModel(
            id=str(uuid7()),
            name=admin_data.name,
            email=normalized_email,
            phone=admin_data.phone,
            password_hash=hash_password(admin_data.password),
            address=address,
            store_id=None,
            role=RoleEnum.ADMIN
        )

        created_admin = self.emploee_repository.create(admin)

        token = create_access_token(data={
            "sub": created_admin.id,
            "email": created_admin.email,
            "role": created_admin.role,
            "store_id": None
        })

        return {
            "message": "Admin criado com sucesso!",
            "id": created_admin.id,
            "email": created_admin.email,
            "access_token": token,
            "token_type": "Bearer"
        }

    async def login(self, email: str, password: str) -> dict:
        normalized_email = email.strip().lower()
        is_employee = normalized_email.endswith("@raizesnordeste.com")

        if is_employee:
            user = self.emploee_repository.get_by_email(email)
            if not user or not verify_password(password, user.password_hash):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email or password is invalid")
            role = user.role
            user_id = user.id
            store_id = user.store_id
        else:
            user = self.costumer_repository.get_by_email(email)
            if not user or not verify_password(password, user.password_hash):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email or password is invalid")
            role = "COSTUMER"
            user_id = user.id
            store_id = None

        token = create_access_token(data={
            "sub": user_id,
            "email": email,
            "role": role,
            "store_id": store_id
        })

        return {
            "id": user_id,
            "access_token": token,
            "token_type": "Bearer"
        }

    async def logout(self) -> dict:
        return {"message": "Logout successful"}
