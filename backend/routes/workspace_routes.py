from flask import Blueprint, request, jsonify
from services.workspace_service import get_user_workspaces, create_workspace, delete_workspace

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

@workspace_bp.route('/api/workspaces/<int:workspace_id>', methods=['DELETE'])
def delete_workspace_route(workspace_id):
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    _, error = delete_workspace(workspace_id, user_id)
    if error:
        status = 403 if 'default' in error else 404
        return jsonify({'error': error}), status
    return jsonify({'message': 'Workspace deleted'}), 200
