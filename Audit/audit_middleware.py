from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from fastapi import Request


class AuditMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, audit_service):
        super().__init__(app)
        self.audit_service = audit_service

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        if hasattr(request.state, 'audit_action'):
            self.audit_service.log(
                action=request.state.audit_action,
                model=request.state.audit_model,
                affected_item_id=request.state.audit_item_id,
                requester_id=request.state.requester_id,
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent"),
                status_code=response.status_code
            )
        return response
