from flask import Blueprint, current_app, request, jsonify

from middlewares.auth import login_required

task_bp = Blueprint('tasks', __name__)


def _controller():
    return current_app.task_controller


@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    payload, status = _controller().list_tasks()
    return jsonify(payload), status


@task_bp.route('/tasks/search', methods=['GET'])
def search_tasks():
    payload, status = _controller().search_tasks(
        query=request.args.get('q', ''),
        status=request.args.get('status', ''),
        priority=request.args.get('priority', ''),
        user_id=request.args.get('user_id', ''),
    )
    return jsonify(payload), status


@task_bp.route('/tasks/stats', methods=['GET'])
def task_stats():
    payload, status = _controller().stats()
    return jsonify(payload), status


@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    payload, status = _controller().get_task(task_id)
    return jsonify(payload), status


@task_bp.route('/tasks', methods=['POST'])
@login_required
def create_task():
    payload, status = _controller().create_task(request.get_json(silent=True))
    return jsonify(payload), status


@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    payload, status = _controller().update_task(task_id, request.get_json(silent=True))
    return jsonify(payload), status


@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    payload, status = _controller().delete_task(task_id)
    return jsonify(payload), status
