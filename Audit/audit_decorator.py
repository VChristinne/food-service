from typing import Callable, Type, Union
from functools import wraps
from fastapi import Request


class AuditDecorator:
    def __init__(self, audit_service):
        self.audit_service = audit_service

    def log(self, action, model_class: Union[Type, str]):
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                request: Request = kwargs.get("request")
                current_user = kwargs.get("current_user")
                result = await func(*args, **kwargs)

                model_name = model_class.__tablename__ if isinstance(model_class, type) else model_class

                request.state.audit_action = action
                request.state.audit_model = model_name
                request.state.audit_item_id = (
                    result.id if hasattr(result, 'id')
                    else result.get("id") if isinstance(result, dict)
                    else "N/A"
                )
                request.state.requester_id = (
                    current_user.get("sub") if isinstance(current_user, dict)
                    else getattr(current_user, "id", "system")
                ) or "system"

                return result
            return wrapper
        return decorator
