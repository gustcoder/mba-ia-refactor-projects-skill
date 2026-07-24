import logging

from flask import jsonify, request

from middlewares.error_handler import DominioError
from models.pedido import STATUS_VALIDOS

logger = logging.getLogger(__name__)


class PedidoController:
    def __init__(self, pedido_model):
        self.pedido_model = pedido_model

    def criar(self):
        dados = request.get_json(silent=True)
        if not dados:
            raise DominioError("Dados inválidos", 400)

        usuario_id = dados.get("usuario_id")
        itens = dados.get("itens", [])

        if not usuario_id:
            raise DominioError("Usuario ID é obrigatório", 400)
        if not itens or len(itens) == 0:
            raise DominioError("Pedido deve ter pelo menos 1 item", 400)

        resultado = self.pedido_model.criar(usuario_id, itens)
        if "erro" in resultado:
            raise DominioError(resultado["erro"], 400)

        logger.info("Pedido %s criado para usuario %s", resultado["pedido_id"], usuario_id)
        logger.info("Notificações de pedido criado (email/sms/push) enviadas para usuario %s", usuario_id)

        return jsonify({
            "dados": resultado,
            "sucesso": True,
            "mensagem": "Pedido criado com sucesso",
        }), 201

    def listar_por_usuario(self, usuario_id):
        pedidos = self.pedido_model.get_by_usuario(usuario_id)
        return jsonify({"dados": pedidos, "sucesso": True}), 200

    def listar_todos(self):
        pedidos = self.pedido_model.get_all()
        return jsonify({"dados": pedidos, "sucesso": True}), 200

    def atualizar_status(self, pedido_id):
        dados = request.get_json(silent=True) or {}
        novo_status = dados.get("status", "")

        if novo_status not in STATUS_VALIDOS:
            raise DominioError("Status inválido", 400)

        self.pedido_model.atualizar_status(pedido_id, novo_status)

        if novo_status == "aprovado":
            logger.info("Pedido %s foi aprovado! Preparar envio.", pedido_id)
        if novo_status == "cancelado":
            logger.info("Pedido %s cancelado. Devolver estoque.", pedido_id)

        return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200

    def relatorio_vendas(self):
        relatorio = self.pedido_model.relatorio_vendas()
        return jsonify({"dados": relatorio, "sucesso": True}), 200
