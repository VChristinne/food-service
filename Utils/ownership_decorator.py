from fastapi import HTTPException, status
from functools import wraps
from typing import Callable


def require_roles(roles: list[str]):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")

            resource_id = kwargs.get("resource_id") or (
                kwargs.get("costumer_id") or
                kwargs.get("employee_id") or
                kwargs.get("inventory_id")
            )

            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Usuário atual não encontrado"
                )

            user_id = str(current_user.get("sub"))
            user_role = current_user.get("role")

            # ownership validation
            if resource_id:
                is_owner = user_id == str(resource_id)
                has_role = user_role in roles and "owner" not in roles

                if not (is_owner or has_role):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Acesso Negado (ownership)"
                    )
            # role validation
            else:
                if user_role not in roles:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Acesso Negado (role)"
                    )

            return await func(*args, **kwargs)
        return wrapper
    return decorator
