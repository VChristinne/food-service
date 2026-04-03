from typing import Callable, Type
from functools import wraps
from fastapi import Request, HTTPException


class AuditDecorator:
    def __init__(self, audit_service):
        self.audit_service = audit_service

    def log(self, action, model_class: Type):
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                request: Request = kwargs.get("request")
                current_user = kwargs.get("current_user")
                result = await func(*args, **kwargs)

                request.state.audit_action = action
                request.state.audit_model = model_class.__tablename__
                request.state.audit_item_id = result.id if hasattr(result, 'id') else result.get("id") if isinstance(result, dict) else None
                request.state.requester_id = current_user.id if current_user else "system"

                return result
            return wrapper
        return decorator
