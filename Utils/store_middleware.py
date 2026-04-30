from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from fastapi import Request
from jwt.exceptions import InvalidTokenError
from fastapi.security import HTTPBearer
from jwt import decode
from os import getenv
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = getenv("SECRET_KEY")
ALGORITHM = getenv("ALGORITHM", "HS256")
security = HTTPBearer(auto_error=False)


class StoreMiddleware(BaseHTTPMiddleware):
    """
    Middleware que extrai automaticamente o store_id do JWT token e adiciona ao request.state.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        auth_header = request.headers.get("Authorization")
        store_id = None

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                store_id = payload.get("store_id")
            except InvalidTokenError:
                pass

        request.state.store_id = store_id
        response = await call_next(request)
        return response
