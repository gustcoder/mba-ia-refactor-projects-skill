import logging

from flask import jsonify, request

from middlewares.auth import gerar_token
from middlewares.error_handler import DominioError

logger = logging.getLogger(__name__)


class UsuarioController:
    def __init__(self, usuario_model):
        self.usuario_model = usuario_model

    def listar(self):
        usuarios = self.usuario_model.get_all()
        return jsonify({"dados": usuarios, "sucesso": True}), 200

    def buscar_por_id(self, usuario_id):
        usuario = self.usuario_model.get_by_id(usuario_id)
        if not usuario:
            raise DominioError("Usuário não encontrado", 404)
        return jsonify({"dados": usuario, "sucesso": True}), 200

    def criar(self):
        dados = request.get_json(silent=True)
        if not dados:
            raise DominioError("Dados inválidos", 400)

        nome = dados.get("nome", "")
        email = dados.get("email", "")
        senha = dados.get("senha", "")

        if not nome or not email or not senha:
            raise DominioError("Nome, email e senha são obrigatórios", 400)

        usuario_id = self.usuario_model.create(nome, email, senha)
        logger.info("Usuário criado: %s", email)
        return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201

    def login(self):
        dados = request.get_json(silent=True) or {}
        email = dados.get("email", "")
        senha = dados.get("senha", "")

        if not email or not senha:
            raise DominioError("Email e senha são obrigatórios", 400)

        usuario = self.usuario_model.autenticar(email, senha)
        if not usuario:
            logger.info("Login falhou: %s", email)
            raise DominioError("Email ou senha inválidos", 401)

        token = gerar_token(usuario)
        logger.info("Login bem-sucedido: %s", email)
        return jsonify({"dados": usuario, "token": token, "sucesso": True, "mensagem": "Login OK"}), 200
