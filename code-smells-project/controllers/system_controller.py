from flask import jsonify

from config import settings


class SystemController:
    def __init__(self, db):
        self.db = db

    def health_check(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT 1")
        cursor.execute("SELECT COUNT(*) FROM produtos")
        produtos = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        usuarios = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        pedidos = cursor.fetchone()[0]

        return jsonify({
            "status": "ok",
            "database": "connected",
            "counts": {
                "produtos": produtos,
                "usuarios": usuarios,
                "pedidos": pedidos,
            },
            "versao": "1.0.0",
            "ambiente": "desenvolvimento" if settings.DEBUG else "producao",
        }), 200
