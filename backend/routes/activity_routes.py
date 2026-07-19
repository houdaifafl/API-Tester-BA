from flask import Blueprint, request, jsonify, g
from services.jwt_service import token_required
from services.activity_service import get_activities

activity_bp = Blueprint('activity', __name__)

@activity_bp.route('/api/workspaces/<int:workspace_id>/activities', methods=['GET'])
@token_required
def get_workspace_activities_route(workspace_id):
    user_id = g.user_id
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)

    if limit < 0 or offset < 0:
        return jsonify({'error': 'Invalid limit or offset'}), 400

    result, error = get_activities(workspace_id, user_id, limit, offset)

    if error:
        if error == 'workspace_not_found':
            return jsonify({'error': 'Workspace not found'}), 404
        if error == 'forbidden':
            return jsonify({'error': 'Forbidden'}), 403
        return jsonify({'error': error}), 400

    return jsonify(result), 200
