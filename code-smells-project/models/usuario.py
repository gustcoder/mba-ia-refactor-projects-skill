from werkzeug.security import check_password_hash, generate_password_hash


class UsuarioModel:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT id, nome, email, tipo, criado_em FROM usuarios")
        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def get_by_id(self, usuario_id):
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT id, nome, email, tipo, criado_em FROM usuarios WHERE id = ?",
            (usuario_id,),
        )
        row = cursor.fetchone()
        return self._row_to_dict(row) if row else None

    def create(self, nome, email, senha, tipo="cliente"):
        senha_hash = generate_password_hash(senha)
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, senha_hash, tipo),
        )
        self.db.commit()
        return cursor.lastrowid

    def autenticar(self, email, senha):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row and check_password_hash(row["senha"], senha):
            return {"id": row["id"], "nome": row["nome"], "email": row["email"], "tipo": row["tipo"]}
        return None

    @staticmethod
    def _row_to_dict(row):
        return {
            "id": row["id"],
            "nome": row["nome"],
            "email": row["email"],
            "tipo": row["tipo"],
            "criado_em": row["criado_em"],
        }
