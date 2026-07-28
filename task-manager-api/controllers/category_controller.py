import logging

from services.errors import NotFoundError, ValidationError

logger = logging.getLogger(__name__)


class CategoryController:
    def __init__(self, category_service):
        self.category_service = category_service

    def list_categories(self):
        return self.category_service.list_categories(), 200

    def create_category(self, data):
        if not data:
            return {'error': 'Dados inválidos'}, 400
        try:
            return self.category_service.create_category(data), 201
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception:
            logger.exception("Erro ao criar categoria")
            return {'error': 'Erro ao criar categoria'}, 500

    def update_category(self, category_id, data):
        if not data:
            return {'error': 'Dados inválidos'}, 400
        try:
            return self.category_service.update_category(category_id, data), 200
        except NotFoundError as e:
            return {'error': str(e)}, 404
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception:
            logger.exception("Erro ao atualizar categoria")
            return {'error': 'Erro ao atualizar'}, 500

    def delete_category(self, category_id):
        try:
            self.category_service.delete_category(category_id)
            return {'message': 'Categoria deletada'}, 200
        except NotFoundError as e:
            return {'error': str(e)}, 404
        except Exception:
            logger.exception("Erro ao deletar categoria")
            return {'error': 'Erro ao deletar'}, 500
