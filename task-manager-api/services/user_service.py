import logging

from models.user import User
from models.task import Task
from services.errors import ConflictError, ForbiddenError, NotFoundError, ValidationError
from utils.helpers import MIN_PASSWORD_LENGTH, VALID_ROLES, validate_email

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db_session):
        self.db = db_session

    def list_users(self):
        return [
            {**u.to_dict(), 'task_count': len(u.tasks)}
            for u in User.query.all()
        ]

    def get_user(self, user_id):
        user = self._find(user_id)
        data = user.to_dict()
        data['tasks'] = [t.to_dict() for t in Task.query.filter_by(user_id=user_id).all()]
        return data

    def get_user_tasks(self, user_id):
        self._find(user_id)
        tasks = Task.query.filter_by(user_id=user_id).all()
        return [
            {
                'id': t.id,
                'title': t.title,
                'description': t.description,
                'status': t.status,
                'priority': t.priority,
                'created_at': str(t.created_at),
                'due_date': str(t.due_date) if t.due_date else None,
                'overdue': t.is_overdue(),
            }
            for t in tasks
        ]

    def create_user(self, data):
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'user')

        if not name:
            raise ValidationError('Nome é obrigatório')
        if not email:
            raise ValidationError('Email é obrigatório')
        if not password:
            raise ValidationError('Senha é obrigatória')
        if not validate_email(email):
            raise ValidationError('Email inválido')
        if len(password) < MIN_PASSWORD_LENGTH:
            raise ValidationError(f'Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres')
        if User.query.filter_by(email=email).first():
            raise ConflictError('Email já cadastrado')
        if role not in VALID_ROLES:
            raise ValidationError('Role inválido')

        user = User()
        user.name = name
        user.email = email
        user.set_password(password)
        user.role = role

        self.db.add(user)
        self.db.commit()
        logger.info("Usuário criado: %s - %s", user.id, user.name)
        return user.to_dict()

    def update_user(self, user_id, data, current_user):
        user = self._find(user_id)

        if current_user.id != user.id and not current_user.is_admin():
            raise ForbiddenError('Você só pode editar seu próprio perfil')

        if 'role' in data and data['role'] != user.role and not current_user.is_admin():
            raise ForbiddenError('Apenas administradores podem alterar o role de um usuário')

        if 'name' in data:
            user.name = data['name']

        if 'email' in data:
            if not validate_email(data['email']):
                raise ValidationError('Email inválido')
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != user_id:
                raise ConflictError('Email já cadastrado')
            user.email = data['email']

        if 'password' in data:
            if len(data['password']) < MIN_PASSWORD_LENGTH:
                raise ValidationError('Senha muito curta')
            user.set_password(data['password'])

        if 'role' in data:
            if data['role'] not in VALID_ROLES:
                raise ValidationError('Role inválido')
            user.role = data['role']

        if 'active' in data:
            user.active = data['active']

        self.db.commit()
        return user.to_dict()

    def delete_user(self, user_id, current_user):
        if not current_user.is_admin():
            raise ForbiddenError('Apenas administradores podem remover usuários')

        user = self._find(user_id)
        for task in Task.query.filter_by(user_id=user_id).all():
            self.db.delete(task)

        self.db.delete(user)
        self.db.commit()
        logger.info("Usuário deletado: %s", user_id)

    def _find(self, user_id):
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError('Usuário não encontrado')
        return user
