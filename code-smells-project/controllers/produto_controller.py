import logging

from flask import jsonify, request

from middlewares.error_handler import DominioError
from models.produto import ProdutoModel

logger = logging.getLogger(__name__)


def _validar_campos_obrigatorios(dados):
    if not dados:
        raise DominioError("Dados inválidos", 400)
    if "nome" not in dados:
        raise DominioError("Nome é obrigatório", 400)
    if "preco" not in dados:
        raise DominioError("Preço é obrigatório", 400)
    if "estoque" not in dados:
        raise DominioError("Estoque é obrigatório", 400)


class ProdutoController:
    def __init__(self, produto_model):
        self.produto_model = produto_model

    def listar(self):
        produtos = self.produto_model.get_all()
        return jsonify({"dados": produtos, "sucesso": True}), 200

    def buscar_por_id(self, produto_id):
        produto = self.produto_model.get_by_id(produto_id)
        if not produto:
            raise DominioError("Produto não encontrado", 404)
        return jsonify({"dados": produto, "sucesso": True}), 200

    def buscar(self):
        termo = request.args.get("q", "")
        categoria = request.args.get("categoria", None)
        preco_min = request.args.get("preco_min", None)
        preco_max = request.args.get("preco_max", None)

        if preco_min:
            preco_min = float(preco_min)
        if preco_max:
            preco_max = float(preco_max)

        resultados = self.produto_model.search(termo, categoria, preco_min, preco_max)
        return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200

    def criar(self):
        dados = request.get_json(silent=True)
        _validar_campos_obrigatorios(dados)

        nome = dados["nome"]
        descricao = dados.get("descricao", "")
        preco = dados["preco"]
        estoque = dados["estoque"]
        categoria = dados.get("categoria", "geral")

        erro = ProdutoModel.validar_completo(nome, preco, estoque, categoria)
        if erro:
            raise DominioError(erro, 400)

        produto_id = self.produto_model.create(nome, descricao, preco, estoque, categoria)
        logger.info("Produto criado com ID: %s", produto_id)
        return jsonify({"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}), 201

    def atualizar(self, produto_id):
        dados = request.get_json(silent=True)

        produto_existente = self.produto_model.get_by_id(produto_id)
        if not produto_existente:
            raise DominioError("Produto não encontrado", 404)

        _validar_campos_obrigatorios(dados)

        nome = dados["nome"]
        descricao = dados.get("descricao", "")
        preco = dados["preco"]
        estoque = dados["estoque"]
        categoria = dados.get("categoria", "geral")

        erro = ProdutoModel.validar_valores(preco, estoque)
        if erro:
            raise DominioError(erro, 400)

        self.produto_model.update(produto_id, nome, descricao, preco, estoque, categoria)
        return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200

    def deletar(self, produto_id):
        produto = self.produto_model.get_by_id(produto_id)
        if not produto:
            raise DominioError("Produto não encontrado", 404)

        self.produto_model.delete(produto_id)
        logger.info("Produto %s deletado", produto_id)
        return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
