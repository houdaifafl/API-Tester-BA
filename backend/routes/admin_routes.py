from flask import Blueprint, request, jsonify, g
from services.jwt_service import token_required
from services.admin_service import (
    get_all_users, suspend_user, reactivate_user, delete_user,
    promote_to_admin, demote_from_admin, get_all_workspaces,
    delete_workspace_by_admin, get_workspace_collections,
    delete_collection_by_admin, log_sensitive_view, get_audit_logs,
    get_user_notifications, mark_notifications_read
)

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/api/admin/users', methods=['GET'])
@token_required
def list_users_route():
    admin_id = g.user_id
    users, error = get_all_users(admin_id)
    if error:
        return jsonify({'error': error}), 403
    return jsonify(users), 200

@admin_bp.route('/api/admin/users/<int:user_id>/suspend', methods=['POST'])
@token_required
def suspend_user_route(user_id):
    admin_id = g.user_id
    success, error = suspend_user(admin_id, user_id)
    if error == 'Forbidden':
        return jsonify({'error': error}), 403
    if error:
        return jsonify({'error': error}), 400
    return jsonify({'message': 'User suspended successfully'}), 200

@admin_bp.route('/api/admin/users/<int:user_id>/reactivate', methods=['POST'])
@token_required
def reactivate_user_route(user_id):
    admin_id = g.user_id
    success, error = reactivate_user(admin_id, user_id)
    if error == 'Forbidden':
        return jsonify({'error': error}), 403
    if error:
        return jsonify({'error': error}), 400
    return jsonify({'message': 'User re-activated successfully'}), 200

@admin_bp.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user_route(user_id):
    admin_id = g.user_id
    success, error = delete_user(admin_id, user_id)
    if error == 'Forbidden':
        return jsonify({'error': error}), 403
    if error:
        return jsonify({'error': error}), 400
    return jsonify({'message': 'User deleted successfully'}), 200

@admin_bp.route('/api/admin/users/<int:user_id>/promote', methods=['POST'])
@token_required
def promote_user_route(user_id):
    admin_id = g.user_id
    success, error = promote_to_admin(admin_id, user_id)
    if error == 'Forbidden':
        return jsonify({'error': error}), 403
    if error:
        return jsonify({'error': error}), 400
    return jsonify({'message': 'User promoted to admin'}), 200

@admin_bp.route('/api/admin/users/<int:user_id>/demote', methods=['POST'])
@token_required
def demote_user_route(user_id):
    admin_id = g.user_id
    success, error = demote_from_admin(admin_id, user_id)
    if error == 'Forbidden':
        return jsonify({'error': error}), 403
    if error:
        return jsonify({'error': error}), 400
    return jsonify({'message': 'User demoted from admin'}), 200

@admin_bp.route('/api/admin/workspaces', methods=['GET'])
@token_required
def list_workspaces_route():
    admin_id = g.user_id
    workspaces, error = get_all_workspaces(admin_id)
    if error:
        return jsonify({'error': error}), 403
    return jsonify(workspaces), 200

@admin_bp.route('/api/admin/workspaces/<int:workspace_id>', methods=['DELETE'])
@token_required
def delete_workspace_route(workspace_id):
    admin_id = g.user_id
    success, error = delete_workspace_by_admin(admin_id, workspace_id)
    if error == 'Forbidden':
        return jsonify({'error': error}), 403
    if error:
        return jsonify({'error': error}), 400
    return jsonify({'message': 'Workspace deleted successfully'}), 200

@admin_bp.route('/api/admin/workspaces/<int:workspace_id>/collections', methods=['GET'])
@token_required
def workspace_collections_route(workspace_id):
    admin_id = g.user_id
    collections, error = get_workspace_collections(admin_id, workspace_id)
    if error:
        return jsonify({'error': error}), 403
    return jsonify(collections), 200

@admin_bp.route('/api/admin/collections/<int:collection_id>', methods=['DELETE'])
@token_required
def delete_collection_route(collection_id):
    admin_id = g.user_id
    success, error = delete_collection_by_admin(admin_id, collection_id)
    if error == 'Forbidden':
        return jsonify({'error': error}), 403
    if error:
        return jsonify({'error': error}), 400
    return jsonify({'message': 'Collection deleted successfully'}), 200

@admin_bp.route('/api/admin/workspaces/<int:workspace_id>/log-view', methods=['POST'])
@token_required
def log_sensitive_view_route(workspace_id):
    admin_id = g.user_id
    data = request.json if request.is_json else {}
    details = data.get('details', '')
    success, error = log_sensitive_view(admin_id, workspace_id, details)
    if error:
        return jsonify({'error': error}), 403
    return jsonify({'message': 'Sensitive view logged'}), 200

@admin_bp.route('/api/admin/audit-logs', methods=['GET'])
@token_required
def audit_logs_route():
    admin_id = g.user_id
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    logs, error = get_audit_logs(admin_id, limit, offset)
    if error:
        return jsonify({'error': error}), 403
    return jsonify(logs), 200

# Notifications endpoints for regular users
@admin_bp.route('/api/notifications', methods=['GET'])
@token_required
def list_notifications():
    user_id = g.user_id
    notifs, error = get_user_notifications(user_id)
    return jsonify(notifs), 200

@admin_bp.route('/api/notifications/read', methods=['POST'])
@token_required
def mark_notifications_read_route():
    user_id = g.user_id
    mark_notifications_read(user_id)
    return jsonify({'message': 'Notifications marked read'}), 200
