import os
from dotenv import load_dotenv
import subprocess

load_dotenv()

cert_path = os.getenv("SSL_CERT_PATH")
key_path = os.getenv("SSL_KEY_PATH")

if not cert_path or not key_path:
    raise ValueError("SSL_CERT_PATH and SSL_KEY_PATH must be set in .env file")

command = [
    "uvicorn",
    "app.main:app",
    "--host", "0.0.0.0",
    "--port", "8000",
    "--ssl-certfile", cert_path,
    "--ssl-keyfile", key_path,
    "--reload"
]

print(f"Running command: {' '.join(command)}")

try:
    subprocess.run(command)
except KeyboardInterrupt:
    print("\nServer stopped by user")
