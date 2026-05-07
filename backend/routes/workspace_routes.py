from flask import Blueprint, request, jsonify
from services.workspace_service import get_user_workspaces, create_workspace, delete_workspace, get_workspace_by_id

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

@workspace_bp.route('/api/workspaces/<workspace_id>', methods=['GET'])
def get_workspace_route(workspace_id):
    if not workspace_id.isdigit():
        return jsonify({'error': 'Invalid workspace ID'}), 400
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    workspace, error = get_workspace_by_id(int(workspace_id), user_id)
    if error == 'not_found':
        return jsonify({'error': 'Workspace not found'}), 404
    if error == 'forbidden':
        return jsonify({'error': 'Forbidden'}), 403
    return jsonify(workspace), 200

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
