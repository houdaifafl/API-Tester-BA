from flask import Blueprint, request, jsonify, g
from services.workspace_service import (
    get_user_workspaces, create_workspace, delete_workspace,
    get_workspace_by_id, leave_workspace, update_workspace_name,
    update_member_role, remove_member, get_workspace_collaborators
)
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
    if len(name) > 100:
        return jsonify({'error': 'Workspace name exceeds maximum length of 100 characters'}), 400
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

@workspace_bp.route('/api/workspaces/<int:workspace_id>', methods=['PATCH'])
@token_required
def rename_workspace_route(workspace_id):
    data = request.json if request.is_json else {}
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Workspace name is required'}), 400
    if len(name) > 100:
        return jsonify({'error': 'Workspace name exceeds maximum length of 100 characters'}), 400
        
    user_id = g.user_id
    result, error = update_workspace_name(workspace_id, user_id, name)
    if error:
        if error == 'not_found':
            return jsonify({'error': 'Workspace not found'}), 404
        if error == 'forbidden':
            return jsonify({'error': 'Forbidden'}), 403
        return jsonify({'error': error}), 400
    return jsonify({'message': 'Workspace renamed successfully'}), 200

@workspace_bp.route('/api/workspaces/<int:workspace_id>/members/<int:target_user_id>', methods=['PATCH'])
@token_required
def update_member_role_route(workspace_id, target_user_id):
    data = request.json if request.is_json else {}
    role = data.get('role')
    if not role:
        return jsonify({'error': 'Role is required'}), 400
    if role not in ['editor', 'viewer']:
        return jsonify({'error': 'Invalid role specified'}), 400
        
    user_id = g.user_id
    result, error = update_member_role(workspace_id, user_id, target_user_id, role)
    if error:
        if error == 'not_found':
            return jsonify({'error': 'Workspace not found'}), 404
        if error == 'membership_not_found':
            return jsonify({'error': 'Membership not found'}), 400
        if error == 'forbidden':
            return jsonify({'error': 'Forbidden'}), 403
        return jsonify({'error': error}), 400
    return jsonify({'message': 'Member role updated successfully'}), 200

@workspace_bp.route('/api/workspaces/<int:workspace_id>/members/<int:target_user_id>', methods=['DELETE'])
@token_required
def remove_member_route(workspace_id, target_user_id):
    user_id = g.user_id
    result, error = remove_member(workspace_id, user_id, target_user_id)
    if error:
        if error == 'not_found':
            return jsonify({'error': 'Workspace not found'}), 404
        if error == 'membership_not_found':
            return jsonify({'error': 'Membership not found'}), 400
        if error == 'forbidden':
            return jsonify({'error': 'Forbidden'}), 403
        return jsonify({'error': error}), 400
    return jsonify({'message': 'Member removed successfully'}), 200

@workspace_bp.route('/api/workspaces/<int:workspace_id>/collaborators', methods=['GET'])
@token_required
def get_workspace_collaborators_route(workspace_id):
    user_id = g.user_id
    result, error = get_workspace_collaborators(workspace_id, user_id)
    if error:
        if error == 'not_found':
            return jsonify({'error': 'Workspace not found'}), 404
        if error == 'forbidden':
            return jsonify({'error': 'Forbidden'}), 403
        return jsonify({'error': error}), 400
    return jsonify(result), 200
