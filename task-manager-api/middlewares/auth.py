from functools import wraps

import jwt
from flask import current_app, g, jsonify, request


def _authenticate_request():
    header = request.headers.get('Authorization', '')
    if not header.startswith('Bearer '):
        return None

    token = header[len('Bearer '):]
    try:
        return current_app.auth_service.verify_token(token)
    except jwt.InvalidTokenError:
        return None


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = _authenticate_request()
        if not user:
            return jsonify({'error': 'Autenticação necessária'}), 401
        g.current_user = user
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @wraps(f)
    @login_required
    def wrapper(*args, **kwargs):
        if not g.current_user.is_admin():
            return jsonify({'error': 'Acesso restrito a administradores'}), 403
        return f(*args, **kwargs)
    return wrapper
