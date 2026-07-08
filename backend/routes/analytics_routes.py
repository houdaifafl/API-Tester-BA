from flask import Blueprint, request, jsonify, g
from services.jwt_service import token_required
from services.analytics_service import get_analytics

analytics_bp = Blueprint('analytics_bp', __name__)


@analytics_bp.route('/api/workspaces/<int:workspace_id>/analytics', methods=['GET'])
@token_required
def get_workspace_analytics(workspace_id):
    current_user_id = g.user_id
    timeframe = request.args.get('timeframe', '24h')

    data, err = get_analytics(workspace_id, current_user_id, timeframe)
    if err:
        if err == "Workspace not found":
            return jsonify({"error": err}), 404
        if err == "Forbidden":
            return jsonify({"error": err}), 403
        if "Invalid timeframe" in err:
            return jsonify({"error": err}), 400
        return jsonify({"error": err}), 500

    return jsonify(data), 200
