def registrar_rotas_pedido(app, controller):
    app.add_url_rule("/pedidos", "criar_pedido", controller.criar, methods=["POST"])
    app.add_url_rule("/pedidos", "listar_todos_pedidos", controller.listar_todos, methods=["GET"])
    app.add_url_rule(
        "/pedidos/usuario/<int:usuario_id>",
        "listar_pedidos_usuario",
        controller.listar_por_usuario,
        methods=["GET"],
    )
    app.add_url_rule(
        "/pedidos/<int:pedido_id>/status",
        "atualizar_status_pedido",
        controller.atualizar_status,
        methods=["PUT"],
    )
    app.add_url_rule("/relatorios/vendas", "relatorio_vendas", controller.relatorio_vendas, methods=["GET"])
