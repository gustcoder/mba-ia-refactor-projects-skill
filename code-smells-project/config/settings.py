import os


def _ler_secret_key():
    secret = os.environ.get("SECRET_KEY")
    if not secret:
        raise RuntimeError(
            "SECRET_KEY não definida. Configure a variável de ambiente SECRET_KEY "
            "antes de iniciar a aplicação (ver .env.example)."
        )
    return secret


SECRET_KEY = _ler_secret_key()
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
