import logging

from sqlalchemy import func

from database import db
from models.category import Category
from models.task import Task
from services.errors import NotFoundError, ValidationError
from utils.helpers import DEFAULT_COLOR, is_valid_color

logger = logging.getLogger(__name__)


class CategoryService:
    def __init__(self, db_session):
        self.db = db_session

    def list_categories(self):
        task_counts = dict(
            db.session.query(Task.category_id, func.count(Task.id))
            .group_by(Task.category_id)
            .all()
        )
        return [
            {**c.to_dict(), 'task_count': task_counts.get(c.id, 0)}
            for c in Category.query.all()
        ]

    def create_category(self, data):
        name = data.get('name')
        if not name:
            raise ValidationError('Nome é obrigatório')

        color = data.get('color', DEFAULT_COLOR)
        if not is_valid_color(color):
            raise ValidationError('Cor inválida, use o formato #RRGGBB')

        category = Category()
        category.name = name
        category.description = data.get('description', '')
        category.color = color

        self.db.add(category)
        self.db.commit()
        return category.to_dict()

    def update_category(self, category_id, data):
        category = self._find(category_id)

        if 'name' in data:
            category.name = data['name']
        if 'description' in data:
            category.description = data['description']
        if 'color' in data:
            if not is_valid_color(data['color']):
                raise ValidationError('Cor inválida, use o formato #RRGGBB')
            category.color = data['color']

        self.db.commit()
        return category.to_dict()

    def delete_category(self, category_id):
        category = self._find(category_id)
        self.db.delete(category)
        self.db.commit()

    def _find(self, category_id):
        category = Category.query.get(category_id)
        if not category:
            raise NotFoundError('Categoria não encontrada')
        return category
