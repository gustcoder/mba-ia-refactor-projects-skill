import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


class DominioError(Exception):
    def __init__(self, mensagem, status_code=400):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status_code = status_code


def registrar_error_handlers(app):
    @app.errorhandler(DominioError)
    def _handle_dominio_error(erro):
        return jsonify({"erro": erro.mensagem, "sucesso": False}), erro.status_code

    @app.errorhandler(Exception)
    def _handle_unexpected_error(erro):
        if isinstance(erro, HTTPException):
            return jsonify({"erro": erro.description}), erro.code
        logger.exception("Erro não tratado")
        return jsonify({"erro": str(erro)}), 500
