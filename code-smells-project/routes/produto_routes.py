def registrar_rotas_produto(app, controller):
    app.add_url_rule("/produtos", "listar_produtos", controller.listar, methods=["GET"])
    app.add_url_rule("/produtos/busca", "buscar_produtos", controller.buscar, methods=["GET"])
    app.add_url_rule("/produtos/<int:produto_id>", "buscar_produto", controller.buscar_por_id, methods=["GET"])
    app.add_url_rule("/produtos", "criar_produto", controller.criar, methods=["POST"])
    app.add_url_rule("/produtos/<int:produto_id>", "atualizar_produto", controller.atualizar, methods=["PUT"])
    app.add_url_rule("/produtos/<int:produto_id>", "deletar_produto", controller.deletar, methods=["DELETE"])
