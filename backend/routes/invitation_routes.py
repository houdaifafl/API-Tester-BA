from flask import Blueprint, request, jsonify, g
from services.invitation_service import (
    create_invitation,
    get_pending_invitations,
    accept_invitation,
    decline_invitation,
    cancel_invitation
)
from services.jwt_service import token_required

invitation_bp = Blueprint('invitation', __name__)

@invitation_bp.route('/api/workspaces/<int:workspace_id>/invitations', methods=['POST'])
@token_required
def create_invitation_route(workspace_id):
    data = request.json if request.is_json else {}
    username = data.get('username')
    role = data.get('role', 'viewer')
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    if len(username) > 100:
        return jsonify({'error': 'Username exceeds maximum length of 100 characters'}), 400
    if role and len(role) > 20:
        return jsonify({'error': 'Role exceeds maximum length of 20 characters'}), 400
        
    user_id = g.user_id
    result, error = create_invitation(workspace_id, user_id, username, role)
    
    if error:
        if error == 'workspace_not_found':
            return jsonify({'error': 'Workspace not found'}), 404
        if error == 'forbidden':
            return jsonify({'error': 'Forbidden'}), 403
        if error == 'user_not_found':
            return jsonify({'error': 'User not found'}), 400
        if error == 'already_member':
            return jsonify({'error': 'User is already a member'}), 400
        if error == 'invitation_pending':
            return jsonify({'error': 'Invitation already pending'}), 400
        if error == 'invalid_role':
            return jsonify({'error': 'Invalid role specified'}), 400
        return jsonify({'error': error}), 400
        
    return jsonify({'message': 'Invitation sent successfully', 'invitation_id': result['id']}), 201

@invitation_bp.route('/api/invitations/pending', methods=['GET'])
@token_required
def list_pending_invitations_route():
    user_id = g.user_id
    result, error = get_pending_invitations(user_id)
    if error:
        return jsonify({'error': error}), 400
    return jsonify(result), 200

@invitation_bp.route('/api/invitations/<int:invitation_id>/accept', methods=['POST'])
@token_required
def accept_invitation_route(invitation_id):
    user_id = g.user_id
    result, error = accept_invitation(invitation_id, user_id)
    
    if error:
        if error == 'not_found':
            return jsonify({'error': 'Invitation not found'}), 404
        if error == 'forbidden':
            return jsonify({'error': 'Forbidden'}), 403
        if error == 'not_pending':
            return jsonify({'error': 'Invitation is not pending'}), 400
        return jsonify({'error': error}), 400
        
    return jsonify({'message': 'Invitation accepted'}), 200

@invitation_bp.route('/api/invitations/<int:invitation_id>/decline', methods=['POST'])
@token_required
def decline_invitation_route(invitation_id):
    user_id = g.user_id
    result, error = decline_invitation(invitation_id, user_id)
    
    if error:
        if error == 'not_found':
            return jsonify({'error': 'Invitation not found'}), 404
        if error == 'forbidden':
            return jsonify({'error': 'Forbidden'}), 403
        if error == 'not_pending':
            return jsonify({'error': 'Invitation is not pending'}), 400
        return jsonify({'error': error}), 400
        
    return jsonify({'message': 'Invitation declined'}), 200

@invitation_bp.route('/api/invitations/<int:invitation_id>', methods=['DELETE'])
@token_required
def cancel_invitation_route(invitation_id):
    user_id = g.user_id
    result, error = cancel_invitation(invitation_id, user_id)
    if error:
        if error == 'not_found':
            return jsonify({'error': 'Invitation not found'}), 404
        if error == 'forbidden':
            return jsonify({'error': 'Forbidden'}), 403
        return jsonify({'error': error}), 400
    return jsonify({'message': 'Invitation cancelled successfully'}), 200
