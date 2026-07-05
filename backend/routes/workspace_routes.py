from flask import Blueprint, request, jsonify, g
from services.workspace_service import get_user_workspaces, create_workspace, delete_workspace, get_workspace_by_id, leave_workspace
from services.jwt_service import token_required

workspace_bp = Blueprint('workspace', __name__)

@workspace_bp.route('/api/workspaces', methods=['GET'])
@token_required
def list_workspaces():
    user_id = g.user_id
    return jsonify(get_user_workspaces(user_id)), 200

@workspace_bp.route('/api/workspaces', methods=['POST'])
@token_required
def create_workspace_route():
    data = request.json if request.is_json else {}
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Workspace name is required'}), 400
    user_id = g.user_id
    return jsonify(create_workspace(user_id, name)), 201

@workspace_bp.route('/api/workspaces/<workspace_id>', methods=['GET'])
@token_required
def get_workspace_route(workspace_id):
    if not workspace_id.isdigit():
        return jsonify({'error': 'Invalid workspace ID'}), 400
    user_id = g.user_id
    workspace, error = get_workspace_by_id(int(workspace_id), user_id)
    if error == 'not_found':
        return jsonify({'error': 'Workspace not found'}), 404
    if error == 'forbidden':
        return jsonify({'error': 'Forbidden'}), 403
    return jsonify(workspace), 200

@workspace_bp.route('/api/workspaces/<int:workspace_id>', methods=['DELETE'])
@token_required
def delete_workspace_route(workspace_id):
    user_id = g.user_id
    _, error = delete_workspace(workspace_id, user_id)
    if error:
        status = 403 if 'default' in error else 404
        return jsonify({'error': error}), status
    return jsonify({'message': 'Workspace deleted'}), 200

@workspace_bp.route('/api/workspaces/<int:workspace_id>/leave', methods=['DELETE'])
@token_required
def leave_workspace_route(workspace_id):
    user_id = g.user_id
    _, error = leave_workspace(workspace_id, user_id)
    if error == 'Owners cannot leave their own workspace':
        return jsonify({'error': error}), 403
    if error:
        return jsonify({'error': error}), 404
    return jsonify({'message': 'You have left the workspace.'}), 200
