import os
from dotenv import load_dotenv

load_dotenv()


def _require_env(name, default=None):
    value = os.environ.get(name, default)
    if value is None:
        raise RuntimeError(f"Variável de ambiente obrigatória não definida: {name}")
    return value


DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
SECRET_KEY = _require_env("SECRET_KEY", "dev-only-insecure-key-do-not-use-in-prod" if DEBUG else None)
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///tasks.db")

JWT_EXPIRATION_SECONDS = int(os.environ.get("JWT_EXPIRATION_SECONDS", "86400"))

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
