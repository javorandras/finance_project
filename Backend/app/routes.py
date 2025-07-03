from fastapi import APIRouter
from app.schemas import TransactionRequest, PredictionResponse
from app.utils import clean_description
from app.categorizer import Categorizer

router = APIRouter()
model = Categorizer()
model.load("models/categorizer.pkl")

@router.get("/")
def read_root():
    return {"message": "Finance Categorizer API is running."}

@router.post("/predict", response_model=PredictionResponse)
def predict_categories(request: TransactionRequest):
    cleaned = [clean_description(desc) for desc in request.descriptions]
    predictions = model.predict(cleaned)
    return PredictionResponse(predictions=predictions.tolist())
