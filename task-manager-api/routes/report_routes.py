from flask import Blueprint, current_app, jsonify

report_bp = Blueprint('reports', __name__)


def _controller():
    return current_app.report_controller


@report_bp.route('/reports/summary', methods=['GET'])
def summary_report():
    payload, status = _controller().summary()
    return jsonify(payload), status


@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
def user_report(user_id):
    payload, status = _controller().user_report(user_id)
    return jsonify(payload), status
