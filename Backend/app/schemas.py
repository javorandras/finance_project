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

class UserFinancialSummary(BaseModel):
    balance: Decimal
    total_income: Decimal
    total_expense: Decimal
    savings: Decimal

    class Config:
        from_attributes = True  # optional: for ORM or model support
        json_encoders = {
            Decimal: lambda v: float(round(v, 2))  # control precision in output
        }

class UserResponse(BaseModel):
    id: int
    email: str
    firstname: str
    lastname: str
    balance: Decimal
    total_income: Decimal
    total_expense: Decimal
    savings: Decimal

class TransactionType(str, Enum):
    income = "income"
    expense = "expense"

class TransactionCreateRequest(BaseModel):
    user_id: int
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