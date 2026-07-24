NOME_MIN_LEN = 2
NOME_MAX_LEN = 200
CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]


class ProdutoModel:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM produtos")
        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def get_by_id(self, produto_id):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
        row = cursor.fetchone()
        return self._row_to_dict(row) if row else None

    def get_many_by_id(self, produto_ids):
        if not produto_ids:
            return {}
        placeholders = ",".join("?" * len(produto_ids))
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM produtos WHERE id IN ({})".format(placeholders), produto_ids)
        return {row["id"]: row for row in cursor.fetchall()}

    def create(self, nome, descricao, preco, estoque, categoria):
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria),
        )
        self.db.commit()
        return cursor.lastrowid

    def update(self, produto_id, nome, descricao, preco, estoque, categoria):
        cursor = self.db.cursor()
        cursor.execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
            (nome, descricao, preco, estoque, categoria, produto_id),
        )
        self.db.commit()

    def delete(self, produto_id):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        self.db.commit()

    def decrementar_estoque(self, cursor, produto_id, quantidade):
        cursor.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            (quantidade, produto_id),
        )

    def search(self, termo=None, categoria=None, preco_min=None, preco_max=None):
        query = "SELECT * FROM produtos WHERE 1=1"
        params = []
        if termo:
            query += " AND (nome LIKE ? OR descricao LIKE ?)"
            like_termo = "%{}%".format(termo)
            params.extend([like_termo, like_termo])
        if categoria:
            query += " AND categoria = ?"
            params.append(categoria)
        if preco_min is not None:
            query += " AND preco >= ?"
            params.append(preco_min)
        if preco_max is not None:
            query += " AND preco <= ?"
            params.append(preco_max)

        cursor = self.db.cursor()
        cursor.execute(query, params)
        return [self._row_to_dict(row) for row in cursor.fetchall()]

    @staticmethod
    def validar_valores(preco, estoque):
        if preco < 0:
            return "Preço não pode ser negativo"
        if estoque < 0:
            return "Estoque não pode ser negativo"
        return None

    @staticmethod
    def validar_completo(nome, preco, estoque, categoria):
        erro = ProdutoModel.validar_valores(preco, estoque)
        if erro:
            return erro
        if len(nome) < NOME_MIN_LEN:
            return "Nome muito curto"
        if len(nome) > NOME_MAX_LEN:
            return "Nome muito longo"
        if categoria not in CATEGORIAS_VALIDAS:
            return "Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS)
        return None

    @staticmethod
    def _row_to_dict(row):
        return {
            "id": row["id"],
            "nome": row["nome"],
            "descricao": row["descricao"],
            "preco": row["preco"],
            "estoque": row["estoque"],
            "categoria": row["categoria"],
            "ativo": row["ativo"],
            "criado_em": row["criado_em"],
        }
