from flask import Blueprint, current_app, g, request, jsonify

from middlewares.auth import login_required

user_bp = Blueprint('users', __name__)


def _controller():
    return current_app.user_controller


@user_bp.route('/users', methods=['GET'])
def get_users():
    payload, status = _controller().list_users()
    return jsonify(payload), status


@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    payload, status = _controller().get_user(user_id)
    return jsonify(payload), status


@user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    payload, status = _controller().get_user_tasks(user_id)
    return jsonify(payload), status


@user_bp.route('/users', methods=['POST'])
def create_user():
    payload, status = _controller().create_user(request.get_json(silent=True))
    return jsonify(payload), status


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    payload, status = _controller().update_user(user_id, request.get_json(silent=True), g.current_user)
    return jsonify(payload), status


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    payload, status = _controller().delete_user(user_id, g.current_user)
    return jsonify(payload), status


@user_bp.route('/login', methods=['POST'])
def login():
    payload, status = _controller().login(request.get_json(silent=True))
    return jsonify(payload), status
