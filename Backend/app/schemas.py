from pydantic import BaseModel, EmailStr, Field, ConfigDict
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
    email: str
    password: str = Field(..., min_length=6)
    firstname: str = Field(..., min_length=1, max_length=50)
    lastname: str = Field(..., min_length=1, max_length=50)

class UserLoginRequest(BaseModel):
    email: str
    password: str

class UserUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    firstname: Optional[str] = Field(None, min_length=1, max_length=50)
    lastname: Optional[str] = Field(None, min_length=1, max_length=50)
    goal: Optional[Decimal] = Field(None, ge=0)

class AdminUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    email: str
    firstname: str
    lastname: str
    logged_in_since: datetime
    is_admin: bool

class AdminUpdateRequest(BaseModel):
    is_admin: bool

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    firstname: str
    lastname: str
    balance: Decimal
    total_income: Decimal
    total_expense: Decimal
    savings: Decimal
    goal: Decimal
    is_admin: bool

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TransactionType(str, Enum):
    income = "income"
    expense = "expense"

class TransactionCreateRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = None
    type: TransactionType

class TransactionUpdateRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    amount: Optional[Decimal] = Field(None, gt=0)
    description: Optional[str] = Field(None, max_length=255)
    date: Optional[datetime] = None
    type: Optional[TransactionType] = None

class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    amount: Decimal
    type: TransactionType
    description: Optional[str] = None
    date: datetime