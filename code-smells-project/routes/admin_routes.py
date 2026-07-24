from flask import jsonify

from middlewares.auth import require_admin


def registrar_rotas_admin(app, db):
    @app.route("/admin/reset-db", methods=["POST"])
    @require_admin
    def reset_database():
        cursor = db.cursor()
        cursor.execute("DELETE FROM itens_pedido")
        cursor.execute("DELETE FROM pedidos")
        cursor.execute("DELETE FROM produtos")
        cursor.execute("DELETE FROM usuarios")
        db.commit()
        return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
