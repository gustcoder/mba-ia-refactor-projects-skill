from flask import Blueprint, current_app, request, jsonify

from middlewares.auth import login_required

category_bp = Blueprint('categories', __name__)


def _controller():
    return current_app.category_controller


@category_bp.route('/categories', methods=['GET'])
def get_categories():
    payload, status = _controller().list_categories()
    return jsonify(payload), status


@category_bp.route('/categories', methods=['POST'])
@login_required
def create_category():
    payload, status = _controller().create_category(request.get_json(silent=True))
    return jsonify(payload), status


@category_bp.route('/categories/<int:cat_id>', methods=['PUT'])
@login_required
def update_category(cat_id):
    payload, status = _controller().update_category(cat_id, request.get_json(silent=True))
    return jsonify(payload), status


@category_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
@login_required
def delete_category(cat_id):
    payload, status = _controller().delete_category(cat_id)
    return jsonify(payload), status
