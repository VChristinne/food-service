from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from jwt import encode, decode
from jwt.exceptions import InvalidTokenError
from time import time
from dotenv import load_dotenv
from os import getenv

load_dotenv()

SECRET_KEY = getenv("SECRET_KEY")
ALGORITHM = getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

security = HTTPBearer(auto_error=False)

def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire = int(time()) + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    payload.update({"exp": expire})
    return encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        return decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

def get_current_user(credentials = Depends(security)) -> dict:
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return payload
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
