from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import jsonify, request

from config import settings

ALGORITHM = "HS256"
EXPIRACAO_HORAS = 8


def gerar_token(usuario):
    payload = {
        "sub": usuario["id"],
        "email": usuario["email"],
        "tipo": usuario["tipo"],
        "exp": datetime.now(timezone.utc) + timedelta(hours=EXPIRACAO_HORAS),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def _extrair_token():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header[len("Bearer "):]


def _autenticar_request():
    token = _extrair_token()
    if not token:
        return None, (jsonify({"erro": "Token de autenticação ausente"}), 401)
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None, (jsonify({"erro": "Token inválido ou expirado"}), 401)
    return payload, None


def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        payload, erro = _autenticar_request()
        if erro:
            return erro
        request.usuario_atual = payload
        return f(*args, **kwargs)

    return wrapper


def require_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        payload, erro = _autenticar_request()
        if erro:
            return erro
        if payload.get("tipo") != "admin":
            return jsonify({"erro": "Acesso restrito a administradores"}), 403
        request.usuario_atual = payload
        return f(*args, **kwargs)

    return wrapper
