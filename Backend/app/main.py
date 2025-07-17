from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router
import os
from pathlib import Path

#FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "Frontend"


app = FastAPI(
    title="Finance Categorizer API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://192.168.0.249:8000",
        "http://192.168.0.249:3000",
        "https://192.168.0.249:3000",
        "https://192.168.0.249:8000",
        "http://localhost:8000",
        "https://localhost:8000"
        "http://localhost:3000",
        "https://localhost:3000",
    ],

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
# Mount the Frontend directory
#app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")