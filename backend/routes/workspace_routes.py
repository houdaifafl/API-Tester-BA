from flask import Blueprint, request, jsonify
from services.workspace_service import get_user_workspaces, create_workspace

workspace_bp = Blueprint('workspace', __name__)

@workspace_bp.route('/api/workspaces', methods=['GET'])
def list_workspaces():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    return jsonify(get_user_workspaces(user_id)), 200

@workspace_bp.route('/api/workspaces', methods=['POST'])
def create_workspace_route():
    data = request.json if request.is_json else {}
    user_id = data.get('user_id')
    name = data.get('name')
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    if not name:
        return jsonify({'error': 'Workspace name is required'}), 400
    return jsonify(create_workspace(user_id, name)), 201
