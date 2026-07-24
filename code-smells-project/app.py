import logging

from flask import Flask, jsonify
from flask_cors import CORS

import database
from config import settings
from controllers.pedido_controller import PedidoController
from controllers.produto_controller import ProdutoController
from controllers.system_controller import SystemController
from controllers.usuario_controller import UsuarioController
from middlewares.error_handler import registrar_error_handlers
from models.pedido import PedidoModel
from models.produto import ProdutoModel
from models.usuario import UsuarioModel
from routes.admin_routes import registrar_rotas_admin
from routes.pedido_routes import registrar_rotas_pedido
from routes.produto_routes import registrar_rotas_produto
from routes.system_routes import registrar_rotas_system
from routes.usuario_routes import registrar_rotas_usuario

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG
    CORS(app)

    db = database.create_connection(settings.DATABASE_PATH)

    produto_model = ProdutoModel(db)
    usuario_model = UsuarioModel(db)
    pedido_model = PedidoModel(db, produto_model)

    produto_controller = ProdutoController(produto_model)
    usuario_controller = UsuarioController(usuario_model)
    pedido_controller = PedidoController(pedido_model)
    system_controller = SystemController(db)

    registrar_rotas_produto(app, produto_controller)
    registrar_rotas_usuario(app, usuario_controller)
    registrar_rotas_pedido(app, pedido_controller)
    registrar_rotas_admin(app, db)
    registrar_rotas_system(app, system_controller)
    registrar_error_handlers(app)

    @app.route("/")
    def index():
        return jsonify({
            "mensagem": "Bem-vindo à API da Loja",
            "versao": "1.0.0",
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        })

    return app


app = create_app()

if __name__ == "__main__":
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print("Rodando em http://localhost:5000")
    print("=" * 50)

    app.run(host="0.0.0.0", port=5000, debug=settings.DEBUG)
