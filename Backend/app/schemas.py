from pydantic import BaseModel, EmailStr, Field
from typing import List
from decimal import Decimal
from datetime import datetime
from enum import Enum
from typing import Optional

class TransactionRequest(BaseModel):
    descriptions: List[str]

class PredictionResponse(BaseModel):
    predictions: List[str]


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    firstname: str
    lastname: str


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserUpdateRequest(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    goal: Optional[Decimal] = Field(None, ge=0)

    class Config:
        orm_mode = True


class AdminUserResponse(BaseModel):
    user_id: int
    email: str
    firstname: str
    lastname: str
    logged_in_since: datetime

class AdminUpdateRequest(BaseModel):
    is_admin: bool

class UserResponse(BaseModel):
    id: int
    email: str
    firstname: str
    lastname: str
    balance: Decimal
    total_income: Decimal
    total_expense: Decimal
    savings: Decimal
    goal: Decimal

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"

class TransactionCreateRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    description: str | None = None
    type: TransactionType

class TransactionUpdateRequest(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0)
    description: Optional[str] = None
    date: Optional[datetime] = None
    type: Optional[str] = Field(None, pattern="^(income|expense)$")

    class Config:
        orm_mode = True


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    amount: Decimal
    type: TransactionType
    description: Optional[str] = None
    date: datetime

    class Config:
        orm_mode = True