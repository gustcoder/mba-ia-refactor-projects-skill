import logging

from services.auth_service import InactiveUserError, InvalidCredentialsError
from services.errors import ConflictError, ForbiddenError, NotFoundError, ValidationError

logger = logging.getLogger(__name__)


class UserController:
    def __init__(self, user_service, auth_service):
        self.user_service = user_service
        self.auth_service = auth_service

    def list_users(self):
        return self.user_service.list_users(), 200

    def get_user(self, user_id):
        try:
            return self.user_service.get_user(user_id), 200
        except NotFoundError as e:
            return {'error': str(e)}, 404

    def get_user_tasks(self, user_id):
        try:
            return self.user_service.get_user_tasks(user_id), 200
        except NotFoundError as e:
            return {'error': str(e)}, 404

    def create_user(self, data):
        if not data:
            return {'error': 'Dados inválidos'}, 400
        try:
            return self.user_service.create_user(data), 201
        except ValidationError as e:
            return {'error': str(e)}, 400
        except ConflictError as e:
            return {'error': str(e)}, 409
        except Exception:
            logger.exception("Erro ao criar usuário")
            return {'error': 'Erro ao criar usuário'}, 500

    def update_user(self, user_id, data, current_user):
        if not data:
            return {'error': 'Dados inválidos'}, 400
        try:
            return self.user_service.update_user(user_id, data, current_user), 200
        except NotFoundError as e:
            return {'error': str(e)}, 404
        except ForbiddenError as e:
            return {'error': str(e)}, 403
        except ValidationError as e:
            return {'error': str(e)}, 400
        except ConflictError as e:
            return {'error': str(e)}, 409
        except Exception:
            logger.exception("Erro ao atualizar usuário")
            return {'error': 'Erro ao atualizar'}, 500

    def delete_user(self, user_id, current_user):
        try:
            self.user_service.delete_user(user_id, current_user)
            return {'message': 'Usuário deletado com sucesso'}, 200
        except NotFoundError as e:
            return {'error': str(e)}, 404
        except ForbiddenError as e:
            return {'error': str(e)}, 403
        except Exception:
            logger.exception("Erro ao deletar usuário")
            return {'error': 'Erro ao deletar'}, 500

    def login(self, data):
        if not data:
            return {'error': 'Dados inválidos'}, 400

        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return {'error': 'Email e senha são obrigatórios'}, 400

        try:
            user = self.auth_service.authenticate(email, password)
        except InvalidCredentialsError:
            return {'error': 'Credenciais inválidas'}, 401
        except InactiveUserError:
            return {'error': 'Usuário inativo'}, 403

        token = self.auth_service.issue_token(user)
        return {
            'message': 'Login realizado com sucesso',
            'user': user.to_dict(),
            'token': token,
        }, 200
