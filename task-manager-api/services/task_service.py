import logging

from sqlalchemy.orm import joinedload

from models.task import Task
from models.user import User
from models.category import Category
from services.errors import NotFoundError, ValidationError
from utils.helpers import (
    VALID_STATUSES,
    MIN_TITLE_LENGTH,
    MAX_TITLE_LENGTH,
    DEFAULT_PRIORITY,
    PRIORITY_MIN,
    PRIORITY_MAX,
    parse_date,
)

logger = logging.getLogger(__name__)


class TaskService:
    def __init__(self, db_session, notification_service=None):
        self.db = db_session
        self.notification_service = notification_service

    def list_tasks(self):
        tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
        return [self._serialize(t) for t in tasks]

    def get_task(self, task_id):
        task = self._find(task_id)
        return self._serialize(task)

    def search_tasks(self, query=None, status=None, priority=None, user_id=None):
        tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category))

        if query:
            tasks = tasks.filter(
                Task.title.like(f'%{query}%') | Task.description.like(f'%{query}%')
            )
        if status:
            tasks = tasks.filter(Task.status == status)
        if priority:
            tasks = tasks.filter(Task.priority == int(priority))
        if user_id:
            tasks = tasks.filter(Task.user_id == int(user_id))

        return [self._serialize(t) for t in tasks.all()]

    def stats(self):
        total = Task.query.count()
        by_status = {
            status: Task.query.filter_by(status=status).count()
            for status in VALID_STATUSES
        }
        overdue = sum(1 for t in Task.query.all() if t.is_overdue())

        return {
            'total': total,
            'pending': by_status['pending'],
            'in_progress': by_status['in_progress'],
            'done': by_status['done'],
            'cancelled': by_status['cancelled'],
            'overdue': overdue,
            'completion_rate': round((by_status['done'] / total) * 100, 2) if total > 0 else 0,
        }

    def create_task(self, data):
        title = self._validate_title(data.get('title'), required=True)
        status = self._validate_status(data.get('status', 'pending'))
        priority = self._validate_priority(data.get('priority', DEFAULT_PRIORITY))
        user_id = data.get('user_id')
        category_id = data.get('category_id')

        user = self._validate_user_exists(user_id) if user_id else None
        self._validate_category_exists(category_id) if category_id else None

        task = Task()
        task.title = title
        task.description = data.get('description', '')
        task.status = status
        task.priority = priority
        task.user_id = user_id
        task.category_id = category_id
        task.due_date = self._parse_due_date(data.get('due_date'))
        task.tags = self._normalize_tags(data.get('tags'))

        self.db.add(task)
        self.db.commit()
        logger.info("Task criada: %s - %s", task.id, task.title)

        if user and self.notification_service:
            self.notification_service.notify_task_assigned(user, task)

        return self._serialize(task)

    def update_task(self, task_id, data):
        task = self._find(task_id)

        if 'title' in data:
            task.title = self._validate_title(data['title'], required=True)
        if 'description' in data:
            task.description = data['description']
        if 'status' in data:
            task.status = self._validate_status(data['status'])
        if 'priority' in data:
            task.priority = self._validate_priority(data['priority'])
        if 'user_id' in data:
            if data['user_id']:
                self._validate_user_exists(data['user_id'])
            task.user_id = data['user_id']
        if 'category_id' in data:
            if data['category_id']:
                self._validate_category_exists(data['category_id'])
            task.category_id = data['category_id']
        if 'due_date' in data:
            task.due_date = self._parse_due_date(data['due_date']) if data['due_date'] else None
        if 'tags' in data:
            task.tags = self._normalize_tags(data['tags'])

        self.db.commit()
        logger.info("Task atualizada: %s", task.id)
        return self._serialize(task)

    def delete_task(self, task_id):
        task = self._find(task_id)
        self.db.delete(task)
        self.db.commit()
        logger.info("Task deletada: %s", task_id)

    def _find(self, task_id):
        task = Task.query.get(task_id)
        if not task:
            raise NotFoundError('Task não encontrada')
        return task

    def _validate_title(self, title, required):
        if not title and required:
            raise ValidationError('Título é obrigatório')
        if title and not (MIN_TITLE_LENGTH <= len(title) <= MAX_TITLE_LENGTH):
            raise ValidationError(
                f'Título deve ter entre {MIN_TITLE_LENGTH} e {MAX_TITLE_LENGTH} caracteres'
            )
        return title

    def _validate_status(self, status):
        if status not in VALID_STATUSES:
            raise ValidationError('Status inválido')
        return status

    def _validate_priority(self, priority):
        if not (PRIORITY_MIN <= priority <= PRIORITY_MAX):
            raise ValidationError(f'Prioridade deve ser entre {PRIORITY_MIN} e {PRIORITY_MAX}')
        return priority

    def _validate_user_exists(self, user_id):
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError('Usuário não encontrado')
        return user

    def _validate_category_exists(self, category_id):
        category = Category.query.get(category_id)
        if not category:
            raise NotFoundError('Categoria não encontrada')
        return category

    def _parse_due_date(self, due_date):
        if not due_date:
            return None
        parsed = parse_date(due_date)
        if not parsed:
            raise ValidationError('Formato de data inválido. Use YYYY-MM-DD')
        return parsed

    def _normalize_tags(self, tags):
        if not tags:
            return tags
        return ','.join(tags) if isinstance(tags, list) else tags

    def _serialize(self, task):
        data = task.to_dict()
        data['overdue'] = task.is_overdue()
        data['user_name'] = task.user.name if task.user else None
        data['category_name'] = task.category.name if task.category else None
        return data
