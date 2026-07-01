from flask import Blueprint, request, jsonify, g
from services.history_service import get_history_entries, create_history_entry
from services.jwt_service import token_required

history_bp = Blueprint('history', __name__)

@history_bp.route('/api/workspaces/<int:workspace_id>/history', methods=['GET'])
@token_required
def list_history(workspace_id):
    user_id = g.user_id
    result, error = get_history_entries(workspace_id, user_id)
    if error == 'not_found':
        return jsonify({'error': 'Workspace not found'}), 404
    if error == 'forbidden':
        return jsonify({'error': 'Forbidden'}), 403
    if error:
        return jsonify({'error': error}), 400
    return jsonify(result), 200

@history_bp.route('/api/workspaces/<int:workspace_id>/history', methods=['POST'])
@token_required
def create_history(workspace_id):
    user_id = g.user_id
    data = request.json if request.is_json else {}
    result, error = create_history_entry(workspace_id, user_id, data)
    if error == 'not_found':
        return jsonify({'error': 'Workspace not found'}), 404
    if error == 'forbidden':
        return jsonify({'error': 'Forbidden'}), 403
    if error:
        return jsonify({'error': error}), 400
    return jsonify(result), 201
