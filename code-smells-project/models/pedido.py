STATUS_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]

FATURAMENTO_LIMITE_DESCONTO_ALTO = 10000
FATURAMENTO_LIMITE_DESCONTO_MEDIO = 5000
FATURAMENTO_LIMITE_DESCONTO_BAIXO = 1000
PERCENTUAL_DESCONTO_ALTO = 0.1
PERCENTUAL_DESCONTO_MEDIO = 0.05
PERCENTUAL_DESCONTO_BAIXO = 0.02


class PedidoModel:
    def __init__(self, db, produto_model):
        self.db = db
        self.produto_model = produto_model

    def criar(self, usuario_id, itens):
        produto_ids = [item["produto_id"] for item in itens]
        produtos_por_id = self.produto_model.get_many_by_id(produto_ids)

        total = 0
        for item in itens:
            produto = produtos_por_id.get(item["produto_id"])
            if produto is None:
                return {"erro": "Produto {} não encontrado".format(item["produto_id"])}
            if produto["estoque"] < item["quantidade"]:
                return {"erro": "Estoque insuficiente para {}".format(produto["nome"])}
            total += produto["preco"] * item["quantidade"]

        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (usuario_id, total),
        )
        pedido_id = cursor.lastrowid

        for item in itens:
            produto = produtos_por_id[item["produto_id"]]
            cursor.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], produto["preco"]),
            )
            self.produto_model.decrementar_estoque(cursor, item["produto_id"], item["quantidade"])

        self.db.commit()
        return {"pedido_id": pedido_id, "total": total}

    def get_by_usuario(self, usuario_id):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,))
        return self._montar_pedidos(cursor.fetchall())

    def get_all(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM pedidos")
        return self._montar_pedidos(cursor.fetchall())

    def atualizar_status(self, pedido_id, novo_status):
        cursor = self.db.cursor()
        cursor.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
        self.db.commit()

    def relatorio_vendas(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        total_pedidos = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(total) FROM pedidos")
        faturamento = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = ?", ("pendente",))
        pendentes = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = ?", ("aprovado",))
        aprovados = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = ?", ("cancelado",))
        cancelados = cursor.fetchone()[0]

        desconto = self._calcular_desconto(faturamento)

        return {
            "total_pedidos": total_pedidos,
            "faturamento_bruto": round(faturamento, 2),
            "desconto_aplicavel": round(desconto, 2),
            "faturamento_liquido": round(faturamento - desconto, 2),
            "pedidos_pendentes": pendentes,
            "pedidos_aprovados": aprovados,
            "pedidos_cancelados": cancelados,
            "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
        }

    def _montar_pedidos(self, rows):
        if not rows:
            return []

        pedido_ids = [row["id"] for row in rows]
        placeholders = ",".join("?" * len(pedido_ids))
        cursor = self.db.cursor()
        cursor.execute(
            """
            SELECT ip.pedido_id, ip.produto_id, ip.quantidade, ip.preco_unitario, p.nome AS produto_nome
            FROM itens_pedido ip
            LEFT JOIN produtos p ON p.id = ip.produto_id
            WHERE ip.pedido_id IN ({})
            """.format(placeholders),
            pedido_ids,
        )
        itens_por_pedido = {}
        for item_row in cursor.fetchall():
            itens_por_pedido.setdefault(item_row["pedido_id"], []).append({
                "produto_id": item_row["produto_id"],
                "produto_nome": item_row["produto_nome"] or "Desconhecido",
                "quantidade": item_row["quantidade"],
                "preco_unitario": item_row["preco_unitario"],
            })

        pedidos = []
        for row in rows:
            pedidos.append({
                "id": row["id"],
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": itens_por_pedido.get(row["id"], []),
            })
        return pedidos

    @staticmethod
    def _calcular_desconto(faturamento):
        if faturamento > FATURAMENTO_LIMITE_DESCONTO_ALTO:
            return faturamento * PERCENTUAL_DESCONTO_ALTO
        if faturamento > FATURAMENTO_LIMITE_DESCONTO_MEDIO:
            return faturamento * PERCENTUAL_DESCONTO_MEDIO
        if faturamento > FATURAMENTO_LIMITE_DESCONTO_BAIXO:
            return faturamento * PERCENTUAL_DESCONTO_BAIXO
        return 0
