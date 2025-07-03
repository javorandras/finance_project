from fastapi import FastAPI
from app.routes import router

app = FastAPI()

# Include all routes from routes.py
app.include_router(router)