from pydantic import BaseModel
from typing import List

class TransactionRequest(BaseModel):
    descriptions: List[str]

class PredictionResponse(BaseModel):
    predictions: List[str]
