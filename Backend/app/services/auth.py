from datetime import datetime, timezone, timedelta
from uuid import uuid4

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.auth import create_access_token
from app.config import settings
from app.models import User, RefreshToken
from app.schemas import UserRegisterRequest, UserLoginRequest
from app.utils import pwd_context


class TokenManager:
    @staticmethod
    def create_refresh_token(user_id: int, db: Session) -> tuple[str, datetime]:
        refresh_token = str(uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        db.add(RefreshToken(user_id=user_id, token=refresh_token, expires_at=expires_at))
        return refresh_token, expires_at


    @staticmethod
    def set_refresh_token_cookie(response: JSONResponse, token: str, expires_at: datetime):
        response.set_cookie(
            key="refresh_token",
            value=token,
            httponly=True,
            secure=settings.SECURE_COOKIES,
            samesite="none",
            expires=expires_at,
            path="/",
            max_age=60 * 60 * 24 * settings.REFRESH_TOKEN_EXPIRE_DAYS
        )


def create_token_response(user_id: int, db: Session) -> JSONResponse:
    access_token = create_access_token({"user_id": user_id})
    refresh_token, expires_at = TokenManager.create_refresh_token(user_id, db)
    db.commit()
    response = JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
    TokenManager.set_refresh_token_cookie(response, refresh_token, expires_at)
    return response


def register_user(user: UserRegisterRequest, db: Session) -> JSONResponse:
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    hashed_password = pwd_context.hash(user.password)
    new_user = User(
        email=user.email,
        password=hashed_password,
        firstname=user.firstname,
        lastname=user.lastname,
        date_created=datetime.now(timezone.utc)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return create_token_response(new_user.id, db)


def login_user(user: UserLoginRequest, db: Session) -> JSONResponse:
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    return create_token_response(db_user.id, db) # type: ignore


def refresh_token_db(token: str, db: Session) -> JSONResponse:
    db_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if not db_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    if db_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        db.delete(db_token)
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

    db.delete(db_token)
    db.commit()

    return create_token_response(db_token.user_id, db) # type: ignore


def logout_user(token: str, db: Session) -> JSONResponse:
    if token:
        db.query(RefreshToken).filter(RefreshToken.token == token).delete()
        db.commit()

    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie("refresh_token", path=f"{settings.V1_PREFIX}/users/refresh")
    return response
