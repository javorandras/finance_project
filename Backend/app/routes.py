from datetime import datetime, timezone, timedelta
from typing import Annotated, List
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status, Depends, Path, Query, Request
from passlib.context import CryptContext
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from starlette.responses import JSONResponse

from app.auth import create_access_token, get_current_user
from app.categorizer import Categorizer
from app.db import engine
from app.finance import update_user_aggregates
from app.schemas import (
    PredictionResponse,
    TokenResponse,
    TransactionCreateRequest,
    TransactionRequest,
    TransactionUpdateRequest,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse, TransactionResponse,
)
from app.utils import clean_description, verify_password

REFRESH_TOKEN_EXPIRE_DAYS = 7
SECURE = False

# API prefix constants
API_V1_PREFIX = "/api/v1"
TRANSACTIONS_PREFIX = "/transactions"
USERS_PREFIX = "/users"
PREDICTIONS_PREFIX = "/predictions"


# Create separate routers
router = APIRouter(prefix=API_V1_PREFIX)
transaction_router = APIRouter(prefix=TRANSACTIONS_PREFIX, tags=["Transactions"])
user_router = APIRouter(prefix=USERS_PREFIX, tags=["Users"])
prediction_router = APIRouter(prefix=PREDICTIONS_PREFIX, tags=["Predictions"])


model = Categorizer()
model.load("models/categorizer.pkl")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/")
def read_root():
    return {"message": "Finance Categorizer API is running."}


@prediction_router.post("/predict", response_model=PredictionResponse)
def predict_categories(request: TransactionRequest):
    cleaned = [clean_description(desc) for desc in request.descriptions]
    predictions = model.predict(cleaned)
    return PredictionResponse(predictions=predictions.tolist())


@user_router.post("/register", response_model=TokenResponse)
def register_user(user: UserRegisterRequest):
    hashed_password = pwd_context.hash(user.password)

    with engine.begin() as conn:
        result = conn.execute(text("SELECT id FROM users WHERE email = :email"), {"email": user.email}).fetchone()
        if result:
            raise HTTPException(status_code=400, detail="Email already registered")

        conn.execute(text("""
            INSERT INTO users (email, password, firstname, lastname, date_created)
            VALUES (:email, :password, :firstname, :lastname, :date_created)
        """), {
            "email": user.email,
            "password": hashed_password,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "date_created": datetime.now(timezone.utc)
        })

        new_user = conn.execute(text("SELECT id FROM users WHERE email = :email"), {"email": user.email}).fetchone()
        user_id = new_user.id

        access_token = create_access_token({"user_id": user_id})
        refresh_token = str(uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        conn.execute(text("INSERT INTO refresh_tokens (user_id, token, expires_at) VALUES (:uid, :token, :exp)"),
                     {"uid": user_id, "token": refresh_token, "exp": expires_at})

        response = JSONResponse(content={
            "access_token": access_token,
            "token_type": "bearer"
        })
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=SECURE,
            samesite="strict",
            expires=expires_at,
            path="/api/v1/users/refresh"
        )
        return response



@user_router.post("/login", response_model=TokenResponse)
def login_user(user: UserLoginRequest):
    with engine.begin() as conn:
        query = text("SELECT * FROM users WHERE email = :email")
        result = conn.execute(query, {"email": user.email}).fetchone()

        if not result or not verify_password(user.password, result.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        user_id = result.id
        access_token = create_access_token({"user_id": user_id})
        refresh_token = str(uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        # Save refresh token
        conn.execute(
            text("INSERT INTO refresh_tokens (user_id, token, expires_at) VALUES (:uid, :token, :exp)"),
            {"uid": user_id, "token": refresh_token, "exp": expires_at}
        )

        response = JSONResponse(content={
            "access_token": access_token,
            "token_type": "bearer"
        })
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=SECURE,
            samesite="strict",
            expires=expires_at,
            path="/api/v1/users/refresh"
        )
        return response



@user_router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: Request):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not found")

    with engine.begin() as conn:
        result = conn.execute(text("""
            SELECT user_id, expires_at FROM refresh_tokens WHERE token = :token
        """), {"token": refresh_token}).fetchone()

        if not result:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        if result.expires_at < datetime.now(timezone.utc):
            conn.execute(text("DELETE FROM refresh_tokens WHERE token = :token"), {"token": refresh_token})
            raise HTTPException(status_code=401, detail="Refresh token expired")

        new_token = str(uuid4())
        new_expiration = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        conn.execute(text("DELETE FROM refresh_tokens WHERE token = :token"), {"token": refresh_token})
        conn.execute(text("INSERT INTO refresh_tokens (user_id, token, expires_at) VALUES (:uid, :token, :exp)"),
                     {"uid": result.user_id, "token": new_token, "exp": new_expiration})

        access_token = create_access_token({"user_id": result.user_id})

        response = JSONResponse(content={
            "access_token": access_token,
            "token_type": "bearer"
        })
        response.set_cookie(
            key="refresh_token",
            value=new_token,
            httponly=True,
            secure=SECURE,
            samesite="strict",
            expires=new_expiration,
            path="/api/v1/users/refresh"
        )
        return response



@user_router.post("/logout")
def logout_user(request: Request):
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token:
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM refresh_tokens WHERE token = :token"), {"token": refresh_token})

    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie("refresh_token", path="/api/v1/users/refresh")
    return response


@user_router.get("/me", response_model=UserResponse)
def get_user_profile(user_id: int = Depends(get_current_user)):
    with engine.connect() as conn:
        query = text("""
            SELECT id, email, firstname, lastname, balance, total_income, total_expense, savings, goal
            FROM users
            WHERE id = :id
        """)
        result = conn.execute(query, {"id": user_id}).fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="User not found")

        # noinspection PyProtectedMember
        return dict(result._mapping)


@transaction_router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    skip: int = Query(0, ge=0, description="Number of transactions to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of transactions to return"),
    current_user: int = Depends(get_current_user),
):
    with engine.connect() as conn:
        query = text("""
            SELECT id, user_id, amount, type, description, date
            FROM transactions
            WHERE user_id = :user_id
            ORDER BY date DESC
            LIMIT :limit OFFSET :skip
        """)
        results = conn.execute(query, {"user_id": current_user, "limit": limit, "skip": skip}).mappings().all()

    transactions = [TransactionResponse(**row) for row in results]
    return transactions


@transaction_router.post("/transaction")
async def create_transaction(
    transaction: TransactionCreateRequest,
    current_user: int = Depends(get_current_user),
):
    with engine.begin() as conn:
        insert_query = text("""
            INSERT INTO transactions (user_id, amount, type, description, date)
            VALUES (:user_id, :amount, :type, :description, :date)
        """)
        conn.execute(insert_query, {
            "user_id": current_user,
            "amount": transaction.amount,
            "type": transaction.type,
            "description": transaction.description or "",
            "date": datetime.now(timezone.utc)
        })

        update_user_aggregates(current_user, conn)

    return {"message": "Transaction added and aggregates updated"}


@transaction_router.put("/transactions/{transaction_id}")
async def update_transaction(
    transaction: TransactionUpdateRequest,
    transaction_id: Annotated[int, Path(gt=0, description="Transaction ID")],
    current_user: int = Depends(get_current_user),
):
    try:
        with engine.begin() as conn:
            query = text("SELECT user_id FROM transactions WHERE id = :id")
            result = conn.execute(query, {"id": transaction_id}).fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Transaction not found")
            user_id = result.user_id

            # Verify ownership
            if user_id != current_user:
                raise HTTPException(status_code=403, detail="Not authorized to update this transaction")

            # Prepare fields to update
            field_map = {
                "amount": transaction.amount,
                "type": transaction.type,
                "description": transaction.description,
                "date": transaction.date
            }

            update_fields = []
            params = {"id": transaction_id}

            for column, value in field_map.items():
                if value is not None:
                    update_fields.append(f"{column} = :{column}")
                    params[column] = value

            if not update_fields:
                raise HTTPException(status_code=400, detail="No fields provided for update")

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
        print(f"Update failed for transaction ID {transaction_id}, user ID {user_id}")
        raise HTTPException(status_code=500, detail="Failed to update transaction")


@transaction_router.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: Annotated[int, Path(gt=0, description="Transaction ID")],
    current_user: int = Depends(get_current_user),
):
    with engine.begin() as conn:
        # Find the transaction to get user_id for aggregates update
        check_stmt = text("SELECT user_id FROM transactions WHERE id = :id")
        result = conn.execute(check_stmt, {"id": transaction_id}).fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Transaction not found")

        user_id = result.user_id

        # Verify ownership
        if user_id != current_user:
            raise HTTPException(status_code=403, detail="Not authorized to delete this transaction")

        # Delete the transaction
        delete_stmt = text("DELETE FROM transactions WHERE id = :id")
        conn.execute(delete_stmt, {"id": transaction_id})
        update_user_aggregates(user_id, conn)

    return {
        "message": f"Transaction with ID {transaction_id} deleted successfully and aggregates updated",
        "transaction_id": transaction_id
    }

__all__ = ["router"]
router.include_router(user_router)
router.include_router(transaction_router)
router.include_router(prediction_router)