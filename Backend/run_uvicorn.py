import os
from dotenv import load_dotenv
import uvicorn

load_dotenv()

cert_path = os.getenv("SSL_CERT_PATH")
key_path = os.getenv("SSL_KEY_PATH")

if not cert_path or not key_path:
    raise ValueError("SSL_CERT_PATH and SSL_KEY_PATH must be set in .env file")

uvicorn.run(
    "app.main:app",
    host="0.0.0.0",
    port=8000,
    ssl_certfile=cert_path,
    ssl_keyfile=key_path,
    reload=True,
)
