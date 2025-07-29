from datetime import datetime, timedelta, timezone
from typing import Dict, Any
import jwt
from fastapi import HTTPException, status
from app.config import settings

class TokenError:
    INVALID_PAYLOAD = "Invalid token payload"
    EXPIRED = "Token has expired"
    INVALID_TOKEN = "Invalid token"

def create_access_token(payload_data: Dict[str, Any], expires_delta: timedelta = None) -> str:
    token_data = payload_data.copy()
    expiration = datetime.now(timezone.utc) + (expires_delta or settings.TOKEN_EXPIRE_DELTA)
    token_data.update({"exp": expiration})
    return jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_access_token(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=TokenError.INVALID_PAYLOAD,
                headers={"WWW-Authenticate": settings.AUTH_HEADER},
            )
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=TokenError.EXPIRED,
            headers={"WWW-Authenticate": settings.AUTH_HEADER},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=TokenError.INVALID_TOKEN,
            headers={"WWW-Authenticate": settings.AUTH_HEADER},
        )