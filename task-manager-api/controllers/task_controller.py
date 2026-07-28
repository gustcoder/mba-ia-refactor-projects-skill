import logging

from services.errors import NotFoundError, ValidationError

logger = logging.getLogger(__name__)


class TaskController:
    def __init__(self, task_service):
        self.task_service = task_service

    def list_tasks(self):
        try:
            return self.task_service.list_tasks(), 200
        except Exception:
            logger.exception("Erro ao listar tasks")
            return {'error': 'Erro interno'}, 500

    def get_task(self, task_id):
        try:
            return self.task_service.get_task(task_id), 200
        except NotFoundError as e:
            return {'error': str(e)}, 404

    def search_tasks(self, query, status, priority, user_id):
        return self.task_service.search_tasks(query, status, priority, user_id), 200

    def stats(self):
        return self.task_service.stats(), 200

    def create_task(self, data):
        if not data:
            return {'error': 'Dados inválidos'}, 400
        try:
            return self.task_service.create_task(data), 201
        except ValidationError as e:
            return {'error': str(e)}, 400
        except NotFoundError as e:
            return {'error': str(e)}, 404
        except Exception:
            logger.exception("Erro ao criar task")
            return {'error': 'Erro ao criar task'}, 500

    def update_task(self, task_id, data):
        if not data:
            return {'error': 'Dados inválidos'}, 400
        try:
            return self.task_service.update_task(task_id, data), 200
        except NotFoundError as e:
            return {'error': str(e)}, 404
        except ValidationError as e:
            return {'error': str(e)}, 400
        except Exception:
            logger.exception("Erro ao atualizar task")
            return {'error': 'Erro ao atualizar'}, 500

    def delete_task(self, task_id):
        try:
            self.task_service.delete_task(task_id)
            return {'message': 'Task deletada com sucesso'}, 200
        except NotFoundError as e:
            return {'error': str(e)}, 404
        except Exception:
            logger.exception("Erro ao deletar task")
            return {'error': 'Erro ao deletar'}, 500
