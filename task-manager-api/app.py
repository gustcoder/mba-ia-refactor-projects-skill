import logging
from datetime import datetime

from flask import Flask
from flask_cors import CORS

import config.settings as settings
from database import db
from routes.task_routes import task_bp
from routes.user_routes import user_bp
from routes.category_routes import category_bp
from routes.report_routes import report_bp
from services.auth_service import AuthService
from services.notification_service import NotificationService
from services.task_service import TaskService
from services.user_service import UserService
from services.category_service import CategoryService
from services.report_service import ReportService
from controllers.task_controller import TaskController
from controllers.user_controller import UserController
from controllers.category_controller import CategoryController
from controllers.report_controller import ReportController

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = settings.SECRET_KEY

CORS(app)
db.init_app(app)

# Composition root: toda dependência concreta é instanciada aqui, uma única vez,
# e injetada nos serviços/controllers que a usam.
app.auth_service = AuthService(settings.SECRET_KEY, settings.JWT_EXPIRATION_SECONDS)
notification_service = NotificationService(
    db.session, settings.SMTP_HOST, settings.SMTP_PORT, settings.SMTP_USER, settings.SMTP_PASSWORD
)

app.task_controller = TaskController(TaskService(db.session, notification_service))
app.user_controller = UserController(UserService(db.session), app.auth_service)
app.category_controller = CategoryController(CategoryService(db.session))
app.report_controller = ReportController(ReportService())

app.register_blueprint(task_bp)
app.register_blueprint(user_bp)
app.register_blueprint(category_bp)
app.register_blueprint(report_bp)


@app.route('/health')
def health():
    return {'status': 'ok', 'timestamp': str(datetime.utcnow())}


@app.route('/')
def index():
    return {'message': 'Task Manager API', 'version': '1.0'}


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=settings.DEBUG, host='0.0.0.0', port=5000)
