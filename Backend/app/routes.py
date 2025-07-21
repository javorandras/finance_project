from datetime import datetime, timezone, timedelta
from typing import Annotated, List
from uuid import uuid4
from fastapi import APIRouter, HTTPException, status, Depends, Path, Query, Request
from passlib.context import CryptContext
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from starlette.responses import JSONResponse, RedirectResponse

from app.auth import create_access_token, get_current_user
from app.categorizer import Categorizer
from app.db import engine
from app.finance import update_user_aggregates
from app.schemas import (
    PredictionResponse, TokenResponse, TransactionCreateRequest,
    TransactionRequest, TransactionUpdateRequest, UserLoginRequest,
    UserRegisterRequest, UserResponse, TransactionResponse,
    UserUpdateRequest, AdminUserResponse, AdminUpdateRequest,
)
from app.utils import clean_description, verify_password


class APIConfig:
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    SECURE = True
    V1_PREFIX = "/api/v1"

    class Endpoints:
        TRANSACTIONS = "/transactions"
        USERS = "/users"
        PREDICTIONS = "/predictions"
        ADMIN = "/admin"


class TokenManager:
    @staticmethod
    def create_refresh_token(user_id: int, conn):
        refresh_token = str(uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(days=APIConfig.REFRESH_TOKEN_EXPIRE_DAYS)
        conn.execute(
            text("INSERT INTO refresh_tokens (user_id, token, expires_at) VALUES (:uid, :token, :exp)"),
            {"uid": user_id, "token": refresh_token, "exp": expires_at}
        )
        return refresh_token, expires_at

    @staticmethod
    def set_refresh_token_cookie(response: JSONResponse, token: str, expires_at: datetime, path: str = "/"):
        response.set_cookie(
            key="refresh_token",
            value=token,
            httponly=True,
            secure=APIConfig.SECURE,
            samesite="none",
            expires=expires_at,
            path=path,
            max_age=60 * 60 * 24 * APIConfig.REFRESH_TOKEN_EXPIRE_DAYS
        )


class TransactionService:
    @staticmethod
    def verify_transaction_ownership(conn, transaction_id: int, current_user: int):
        query = text("SELECT user_id FROM transactions WHERE id = :id")
        result = conn.execute(query, {"id": transaction_id}).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Transaction not found")
        if result.user_id != current_user:
            raise HTTPException(status_code=403, detail="Not authorized to access this transaction")
        return result.user_id

    @staticmethod
    def prepare_update_fields(transaction: TransactionUpdateRequest):
        field_map = {
            "amount": transaction.amount,
            "type": transaction.type,
            "description": transaction.description,
            "date": transaction.date
        }
        update_fields = []
        params = {}

        for column, value in field_map.items():
            if value is not None:
                update_fields.append(f"{column} = :{column}")
                params[column] = value

        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields provided for update")
        return update_fields, params


# Initialize components
router = APIRouter(prefix=APIConfig.V1_PREFIX)
transaction_router = APIRouter(prefix=APIConfig.Endpoints.TRANSACTIONS, tags=["Transactions"])
user_router = APIRouter(prefix=APIConfig.Endpoints.USERS, tags=["Users"])
prediction_router = APIRouter(prefix=APIConfig.Endpoints.PREDICTIONS, tags=["Predictions"])

admin_router = APIRouter(prefix=APIConfig.Endpoints.ADMIN, tags=["Admin"])


model = Categorizer()
model.load("models/categorizer.pkl")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
token_manager = TokenManager()
transaction_service = TransactionService()


@router.get("/")
async def redirect_to_frontend():
    return RedirectResponse(url="/index.html")


@prediction_router.post("/predict", response_model=PredictionResponse)
def predict_categories(request: TransactionRequest):
    cleaned = [clean_description(desc) for desc in request.descriptions]
    predictions = model.predict(cleaned)
    return PredictionResponse(predictions=predictions.tolist())


@user_router.post("/register", response_model=TokenResponse)
def register_user(user: UserRegisterRequest):
    hashed_password = pwd_context.hash(user.password)

    with engine.begin() as conn:
        if conn.execute(text("SELECT id FROM users WHERE email = :email"),
                        {"email": user.email}).fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")

        conn.execute(
            text("""
                 INSERT INTO users (email, password, firstname, lastname, date_created)
                 VALUES (:email, :password, :firstname, :lastname, :date_created)
                 """),
            {
                "email": user.email,
                "password": hashed_password,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "date_created": datetime.now(timezone.utc)
            }
        )

        user_id = conn.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": user.email}
        ).fetchone().id

        access_token = create_access_token({"user_id": user_id})
        refresh_token, expires_at = token_manager.create_refresh_token(user_id, conn)

        response = JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
        token_manager.set_refresh_token_cookie(response, refresh_token, expires_at)
        return response


@user_router.post("/login", response_model=TokenResponse)
def login_user(user: UserLoginRequest):
    with engine.begin() as conn:
        result = conn.execute(
            text("SELECT * FROM users WHERE email = :email"),
            {"email": user.email}
        ).fetchone()

        if not result or not verify_password(user.password, result.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        access_token = create_access_token({"user_id": result.id})
        refresh_token, expires_at = token_manager.create_refresh_token(result.id, conn)

        response = JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
        token_manager.set_refresh_token_cookie(response, refresh_token, expires_at)
        return response


@user_router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: Request):
    refresh_token_from_req = request.cookies.get("refresh_token")
    if not refresh_token_from_req:
        raise HTTPException(status_code=401, detail="Refresh token not found")

    with engine.begin() as conn:
        result = conn.execute(
            text("""
                SELECT user_id, expires_at
                FROM refresh_tokens 
                WHERE token = :token
            """),
            {"token": refresh_token_from_req}
        ).fetchone()

        if not result:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
            
        expires_at = result.expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            conn.execute(text("DELETE FROM refresh_tokens WHERE token = :token"),
                         {"token": refresh_token_from_req})
            raise HTTPException(status_code=401, detail="Refresh token expired")

        access_token = create_access_token({"user_id": result.user_id})
        new_token, new_expiration = token_manager.create_refresh_token(result.user_id, conn)

        conn.execute(text("DELETE FROM refresh_tokens WHERE token = :token"),
                     {"token": refresh_token_from_req})

        response = JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
        token_manager.set_refresh_token_cookie(response, new_token, new_expiration)
        return response


@user_router.post("/logout")
def logout_user(request: Request):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM refresh_tokens WHERE token = :token"),
                         {"token": refresh_token})

    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie("refresh_token", path=f"{APIConfig.V1_PREFIX}/users/refresh")
    return response

@admin_router.get("/users", response_model=List[AdminUserResponse])
async def get_logged_in_users(current_user: int = Depends(get_current_user)):
        with engine.begin() as conn:
            # Check if the current user is an admin
            admin_check = conn.execute(
                text("SELECT is_admin FROM users WHERE id = :id"),
                {"id": current_user}
            ).fetchone()

            if not admin_check or not admin_check.is_admin:
                raise HTTPException(status_code=403, detail="Admin access required")

            # Get all users with active refresh tokens
            results = conn.execute(
                text("""
                     SELECT u.id               as user_id,
                            u.email,
                            u.firstname,
                            u.lastname,
                            MIN(rt.created_at) as logged_in_since
                     FROM users u
                              JOIN refresh_tokens rt ON u.id = rt.user_id
                     WHERE rt.expires_at > NOW()
                     GROUP BY u.id, u.email, u.firstname, u.lastname
                     ORDER BY logged_in_since DESC
                     """)
            ).mappings().all()

            return list(results)


@admin_router.put("/users/{user_id}/admin")
def set_user_admin(
    user_id: int,
    update: AdminUpdateRequest,
    current_user: int = Depends(get_current_user)
):
    with engine.begin() as conn:
        # Admin check
        admin_check = conn.execute(
            text("SELECT is_admin FROM users WHERE id = :id"),
            {"id": current_user}
        ).fetchone()
        if not admin_check or not admin_check.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")

        # Cannot demote yourself
        if user_id == current_user and not update.is_admin:
            raise HTTPException(status_code=400, detail="Cannot remove admin rights from yourself")

        result = conn.execute(
            text("UPDATE users SET is_admin = :is_admin WHERE id = :user_id"),
            {"is_admin": update.is_admin, "user_id": user_id}
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")

    return {"message": f"User {user_id} admin status set to {update.is_admin}"}


@user_router.get("/me", response_model=UserResponse)
def get_user_profile(user_id: int = Depends(get_current_user)):
    with engine.begin() as conn:
        result = conn.execute(
            text("""
                 SELECT id,
                        email,
                        firstname,
                        lastname,
                        balance,
                        total_income,
                        total_expense,
                        savings,
                        goal
                 FROM users
                 WHERE id = :id
                 """),
            {"id": user_id}
        ).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        return dict(result._mapping)


@admin_router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user: int = Depends(get_current_user)
):
    with engine.begin() as conn:
        admin_check = conn.execute(
            text("SELECT is_admin FROM users WHERE id = :id"),
            {"id": current_user}
        ).fetchone()
        if not admin_check or not admin_check.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")

        # Prevent deleting self
        if user_id == current_user:
            raise HTTPException(status_code=400, detail="Cannot delete your own user")

        # Delete related refresh tokens
        conn.execute(text("DELETE FROM refresh_tokens WHERE user_id = :user_id"), {"user_id": user_id})
        # Delete related transactions
        conn.execute(text("DELETE FROM transactions WHERE user_id = :user_id"), {"user_id": user_id})
        # Delete user
        result = conn.execute(text("DELETE FROM users WHERE id = :user_id"), {"user_id": user_id})

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")

    return {"message": f"User {user_id} deleted successfully"}



@user_router.put("/me", response_model=UserResponse)
async def update_user_profile(
    update_data: UserUpdateRequest,
    current_user: int = Depends(get_current_user)
):
    with engine.begin() as conn:
        conn.execute(
            text("""
                UPDATE users 
                SET firstname = :firstname,
                    lastname = :lastname,
                    goal = :goal
                WHERE id = :id
                """),
            {
                "firstname": update_data.firstname,
                "lastname": update_data.lastname,
                "goal": update_data.goal,
                "id": current_user
            }
        )
    return get_user_profile(current_user)


@transaction_router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
        skip: int = Query(0, ge=0, description="Number of transactions to skip"),
        limit: int = Query(10, ge=1, le=100, description="Maximum number of transactions to return"),
        current_user: int = Depends(get_current_user)
):
    with engine.begin() as conn:
        results = conn.execute(
            text("""
                 SELECT id, user_id, amount, type, description, date
                 FROM transactions
                 WHERE user_id = :user_id
                 ORDER BY date DESC
                     LIMIT :limit
                 OFFSET :skip
                 """),
            {"user_id": current_user, "limit": limit, "skip": skip}
        ).mappings().all()
    return [TransactionResponse(**row) for row in results]


@transaction_router.post("/transaction")
async def create_transaction(
        transaction: TransactionCreateRequest,
        current_user: int = Depends(get_current_user)
):
    with engine.begin() as conn:
        conn.execute(
            text("""
                 INSERT INTO transactions (user_id, amount, type, description, date)
                 VALUES (:user_id, :amount, :type, :description, :date)
                 """),
            {
                "user_id": current_user,
                "amount": transaction.amount,
                "type": transaction.type,
                "description": transaction.description or "",
                "date": datetime.now(timezone.utc)
            }
        )
        update_user_aggregates(current_user, conn)
    return {"message": "Transaction added and aggregates updated"}


@transaction_router.put("/transactions/{transaction_id}")
async def update_transaction(
        transaction: TransactionUpdateRequest,
        transaction_id: Annotated[int, Path(gt=0, description="Transaction ID")],
        current_user: int = Depends(get_current_user)
):
    try:
        with engine.begin() as conn:
            user_id = transaction_service.verify_transaction_ownership(conn, transaction_id, current_user)
            update_fields, params = transaction_service.prepare_update_fields(transaction)

            params["id"] = transaction_id
            update_query = text(f"""
                UPDATE transactions
                SET {', '.join(update_fields)}
                WHERE id = :id
            """)

            conn.execute(update_query, params)
            update_user_aggregates(user_id, conn)

        return {
            "message": f"Transaction with ID {transaction_id} updated successfully and aggregates updated",
            "transaction_id": transaction_id
        }
    except SQLAlchemyError as e:
        print(f"Update error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update transaction")


@transaction_router.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
        transaction_id: Annotated[int, Path(gt=0, description="Transaction ID")],
        current_user: int = Depends(get_current_user)
):
    with engine.begin() as conn:
        user_id = transaction_service.verify_transaction_ownership(conn, transaction_id, current_user)
        conn.execute(text("DELETE FROM transactions WHERE id = :id"), {"id": transaction_id})
        update_user_aggregates(user_id, conn)

    return {
        "message": f"Transaction with ID {transaction_id} deleted successfully and aggregates updated",
        "transaction_id": transaction_id
    }


# Register routers
router.include_router(user_router)
router.include_router(transaction_router)
router.include_router(prediction_router)
router.include_router(admin_router)

__all__ = ["router"]