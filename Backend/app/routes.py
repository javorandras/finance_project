from fastapi import APIRouter, HTTPException, status, Depends, Path
from app.schemas import TransactionRequest, PredictionResponse
from app.utils import clean_description
from app.categorizer import Categorizer
from sqlalchemy import insert, select, text
from sqlalchemy.exc import SQLAlchemyError
from app.schemas import UserRegisterRequest
from passlib.context import CryptContext
from datetime import datetime, timezone
from app.schemas import UserLoginRequest
from app.utils import verify_password
from app.finance import update_user_aggregates
from app.schemas import TransactionCreateRequest
from app.schemas import TransactionUpdateRequest
from app.db import engine
from typing import Annotated


# API prefix constants
API_V1_PREFIX = "/api/v1"
TRANSACTIONS_PREFIX = "/transactions"
USERS_PREFIX = "/users"
PREDICTIONS_PREFIX = "/predictions"


# Create separate routers for different functionalities
router = APIRouter(prefix=API_V1_PREFIX)
transaction_router = APIRouter(prefix=TRANSACTIONS_PREFIX, tags=["Transactions"])
user_router = APIRouter(prefix=USERS_PREFIX, tags=["Users"])
prediction_router = APIRouter(prefix=PREDICTIONS_PREFIX, tags=["Predictions"])


# Include sub-routers
router.include_router(transaction_router)
router.include_router(user_router)
router.include_router(prediction_router)



model = Categorizer()
model.load("models/categorizer.pkl")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/")
def read_root():
    return {"message": "Finance Categorizer API is running."}


@router.post("/predict", response_model=PredictionResponse)
def predict_categories(request: TransactionRequest):
    cleaned = [clean_description(desc) for desc in request.descriptions]
    predictions = model.predict(cleaned)
    return PredictionResponse(predictions=predictions.tolist())


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserRegisterRequest):
    hashed_password = pwd_context.hash(user.password)

    with engine.connect() as conn:
        # Check if email already exists
        check_stmt = text("SELECT id FROM users WHERE email = :email")
        result = conn.execute(check_stmt, {"email": user.email}).fetchone()
        if result:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Insert new user
        insert_stmt = text("""
            INSERT INTO users (email, password, firstname, lastname, date_created)
            VALUES (:email, :password, :firstname, :lastname, :date_created)
        """)

        try:
            conn.execute(insert_stmt, {
                "email": user.email,
                "password": hashed_password,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "date_created": datetime.now(timezone.utc)
            })
            conn.commit()
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail="Failed to register user")

    return {"message": "User registered successfully"}

@router.post("/login")
def login_user(user: UserLoginRequest):
    try:
        with engine.connect() as conn:
            query = text("SELECT * FROM users WHERE email = :email")
            result = conn.execute(query, {"email": user.email})
            db_user = result.fetchone()

            if not db_user:
                raise HTTPException(status_code=401, detail="Invalid email or password")

            if not verify_password(user.password, db_user.password):
                raise HTTPException(status_code=401, detail="Invalid email or password")

            # Optional: Update last_login timestamp
            update_query = text("UPDATE users SET last_login = NOW() WHERE id = :id")
            conn.execute(update_query, {"id": db_user.id})
            conn.commit()

            return {
                "message": "Login successful",
                "user": {
                    "id": db_user.id,
                    "email": db_user.email,
                    "firstname": db_user.firstname,
                    "lastname": db_user.lastname,
                }
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transaction")
async def create_transaction(transaction: TransactionCreateRequest):
    try:
        with engine.begin() as conn:
            insert_query = text("""
                INSERT INTO transactions (user_id, amount, type, description, date)
                VALUES (:user_id, :amount, :type, :description, :date)
            """)
            conn.execute(insert_query, {
                "user_id": transaction.user_id,
                "amount": transaction.amount,
                "type": transaction.type,
                "description": transaction.description or "",
                "date": datetime.now(timezone.utc)
            })

            # Call aggregate update passing the current connection
            update_user_aggregates(transaction.user_id, conn)

        return {"message": "Transaction added and aggregates updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add transaction: {e}")

@router.put("/transactions/{transaction_id}")
async def update_transaction(
    transaction: TransactionUpdateRequest,
    transaction_id: Annotated[int, Path(gt=0, description="Transaction ID")],
):
    try:
        with engine.begin() as conn:
            query = text("SELECT user_id FROM transactions WHERE id = :id")
            result = conn.execute(query, {"id": transaction_id}).fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Transaction not found")
            user_id = result.user_id

            # Define mappings between model fields and DB columns
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


@router.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(transaction_id: Annotated[int, Path(gt=0, description="Transaction ID")]):
    with engine.begin() as conn:
        # Find the transaction to get user_id for aggregates update
        check_stmt = text("SELECT user_id FROM transactions WHERE id = :id")
        result = conn.execute(check_stmt, {"id": transaction_id}).fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Transaction not found")

        user_id = result.user_id

        # Delete the transaction
        delete_stmt = text("DELETE FROM transactions WHERE id = :id")
        conn.execute(delete_stmt, {"id": transaction_id})
        update_user_aggregates(user_id, conn)

    return {
        "message": f"Transaction with ID {transaction_id} deleted successfully and aggregates updated",
        "transaction_id": transaction_id
    }
