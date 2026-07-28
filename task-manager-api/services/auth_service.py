import jwt
from datetime import datetime, timedelta, timezone

from models.user import User


class InvalidCredentialsError(Exception):
    pass


class InactiveUserError(Exception):
    pass


class AuthService:
    def __init__(self, secret_key, expiration_seconds):
        self.secret_key = secret_key
        self.expiration_seconds = expiration_seconds

    def authenticate(self, email, password):
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            raise InvalidCredentialsError()
        if not user.active:
            raise InactiveUserError()
        return user

    def issue_token(self, user):
        payload = {
            'sub': str(user.id),
            'role': user.role,
            'exp': datetime.now(timezone.utc) + timedelta(seconds=self.expiration_seconds),
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')

    def verify_token(self, token):
        payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
        return User.query.get(int(payload['sub']))
