from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv


class AuthConfig:
    load_dotenv()
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    TOKEN_EXPIRE_MINUTES: int = 15
    TOKEN_EXPIRE_SECONDS: int = 0
    AUTH_HEADER: str = "Bearer"

    @classmethod
    def get_default_expiration(cls) -> timedelta:
        return timedelta(minutes=cls.TOKEN_EXPIRE_MINUTES,
                         seconds=cls.TOKEN_EXPIRE_SECONDS)


class TokenError:
    INVALID_PAYLOAD = "Invalid token payload"
    EXPIRED = "Token has expired"
    INVALID_TOKEN = "Invalid token"


def create_access_token(payload_data: Dict[str, Any],
                        expires_delta: Optional[timedelta] = None) -> str:
    token_data = payload_data.copy()
    expiration = datetime.now(timezone.utc) + (
            expires_delta or AuthConfig.get_default_expiration()
    )
    token_data.update({"exp": expiration})
    return jwt.encode(token_data, AuthConfig.SECRET_KEY,
                      algorithm=AuthConfig.ALGORITHM)


def handle_token_validation_error(error_message: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=error_message,
        headers={"WWW-Authenticate": AuthConfig.AUTH_HEADER},
    )


def verify_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, AuthConfig.SECRET_KEY,
                             algorithms=[AuthConfig.ALGORITHM])
        user_id: Optional[int] = payload.get("user_id")

        if user_id is None:
            handle_token_validation_error(TokenError.INVALID_PAYLOAD)
        return user_id
    except jwt.ExpiredSignatureError:
        handle_token_validation_error(TokenError.EXPIRED)
    except jwt.PyJWTError:
        handle_token_validation_error(TokenError.INVALID_TOKEN)


bearer_scheme = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials =
                     Depends(bearer_scheme)) -> int:
    return verify_access_token(credentials.credentials)
