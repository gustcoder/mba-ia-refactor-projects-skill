def registrar_rotas_usuario(app, controller):
    app.add_url_rule("/usuarios", "listar_usuarios", controller.listar, methods=["GET"])
    app.add_url_rule("/usuarios/<int:usuario_id>", "buscar_usuario", controller.buscar_por_id, methods=["GET"])
    app.add_url_rule("/usuarios", "criar_usuario", controller.criar, methods=["POST"])
    app.add_url_rule("/login", "login", controller.login, methods=["POST"])
