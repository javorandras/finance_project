from fastapi import APIRouter, Depends, FastAPI
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.config import settings
from app.dependencies import get_db, get_admin_user, get_refresh_token, get_current_user
from app.services.auth import register_user, login_user, refresh_token_db, logout_user
from app.services.users import get_user_profile, update_user_profile
from app.services.transactions import get_transactions, create_transaction, update_transaction, delete_transaction
from app.services.admin import get_logged_in_users, set_user_admin, delete_user, logout_all_users
from app.schemas import (
    PredictionResponse, TokenResponse, TransactionCreateRequest,
    TransactionUpdateRequest, UserLoginRequest, UserRegisterRequest,
    UserResponse, UserUpdateRequest, AdminUserResponse, AdminUpdateRequest,
    TransactionRequest, TransactionResponse
)
from app.categorizer import Categorizer
from app.utils import clean_description

app = FastAPI()
router = APIRouter(prefix=settings.V1_PREFIX)
transaction_router = APIRouter(prefix=settings.Endpoints.TRANSACTIONS, tags=["Transactions"])
user_router = APIRouter(prefix=settings.Endpoints.USERS, tags=["Users"])
prediction_router = APIRouter(prefix=settings.Endpoints.PREDICTIONS, tags=["Predictions"])
admin_router = APIRouter(prefix=settings.Endpoints.ADMIN, tags=["Admin"])

model = Categorizer()
model.load("models/categorizer.pkl")


@router.get("/")
async def redirect_to_frontend():
    return RedirectResponse(url="/index.html")


@prediction_router.post("/predict", response_model=PredictionResponse)
def predict_categories(request: TransactionRequest):
    cleaned = [clean_description(desc) for desc in request.descriptions]
    predictions = model.predict(cleaned)
    return PredictionResponse(predictions=predictions.tolist())


@user_router.post("/register", response_model=TokenResponse)
def register(user: UserRegisterRequest, db: Session = Depends(get_db)):
    return register_user(user, db)


@user_router.post("/login", response_model=TokenResponse)
def login(user: UserLoginRequest, db: Session = Depends(get_db)):
    return login_user(user, db)


@user_router.post("/refresh", response_model=TokenResponse)
def refresh(token: str = Depends(get_refresh_token), db: Session = Depends(get_db)):
    return refresh_token_db(token, db)


@user_router.post("/logout")
def logout(token: str = Depends(get_refresh_token), db: Session = Depends(get_db)):
    return logout_user(token, db)


@user_router.get("/me", response_model=UserResponse)
def get_profile(user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_user_profile(user_id, db)


@user_router.put("/me", response_model=UserResponse)
async def update_profile(update_data: UserUpdateRequest, user_id: int = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    return update_user_profile(update_data, user_id, db)


@transaction_router.get("/transactions", response_model=list[TransactionResponse])
async def list_transactions(
        skip: int = 0,
        limit: int = 10,
        user_id: int = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    return get_transactions(user_id, skip, limit, db)


@transaction_router.post("/transaction")
async def add_transaction(
        transaction: TransactionCreateRequest,
        user_id: int = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    return create_transaction(transaction, user_id, db)


@transaction_router.put("/transactions/{transaction_id}")
async def update_transaction_endpoint(
        transaction: TransactionUpdateRequest,
        transaction_id: int,
        user_id: int = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    return update_transaction(transaction, transaction_id, user_id, db)


@transaction_router.delete("/transactions/{transaction_id}", status_code=204)
async def delete_transaction_endpoint(
        transaction_id: int,
        user_id: int = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    return delete_transaction(transaction_id, user_id, db)


@admin_router.get("/users", response_model=list[AdminUserResponse])
async def list_logged_in_users(_: int = Depends(get_admin_user), db: Session = Depends(get_db)):
    return get_logged_in_users(db)


@admin_router.put("/users/{user_id}/admin")
def update_user_admin(
        user_id: int,
        update: AdminUpdateRequest,
        current_user: int = Depends(get_admin_user),
        db: Session = Depends(get_db)
):
    return set_user_admin(user_id, update, current_user, db)


@admin_router.delete("/users/{user_id}", status_code=204)
def delete_user_endpoint(
        user_id: int,
        current_user: int = Depends(get_admin_user),
        db: Session = Depends(get_db)
):
    return delete_user(user_id, current_user, db)


@admin_router.post("/logout_all")
def logout_all(_: int = Depends(get_admin_user), db: Session = Depends(get_db)):
    return logout_all_users(db)


router.include_router(user_router)
router.include_router(transaction_router)
router.include_router(prediction_router)
router.include_router(admin_router)
app.include_router(router)

__all__ = ["router"]
