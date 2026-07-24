def registrar_rotas_system(app, controller):
    app.add_url_rule("/health", "health_check", controller.health_check, methods=["GET"])
