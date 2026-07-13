from flask import Blueprint, request, jsonify, g
from services.comment_service import get_comments, create_comment, edit_comment, delete_comment
from services.jwt_service import token_required

comment_bp = Blueprint('comment', __name__)

@comment_bp.route('/api/workspaces/<int:workspace_id>/comments', methods=['GET'])
@token_required
def list_comments_route(workspace_id):
    request_id_val = request.args.get('request_id')
    request_id = int(request_id_val) if (request_id_val and request_id_val.isdigit()) else None

    result, error = get_comments(workspace_id, g.user_id, request_id)
    if error:
        status = 403 if error == "Forbidden" else 404
        return jsonify({'error': error}), status
    return jsonify(result), 200

@comment_bp.route('/api/workspaces/<int:workspace_id>/comments', methods=['POST'])
@token_required
def create_comment_route(workspace_id):
    data = request.json if request.is_json else {}
    content = data.get('content')
    parent_id = data.get('parent_id')
    request_id = data.get('request_id')
    target_tab = data.get('target_tab')
    target_key = data.get('target_key')

    if not content:
        return jsonify({'error': 'Content is required'}), 400
    if len(content) > 2000:
        return jsonify({'error': 'Content exceeds maximum length of 2000 characters'}), 400
    if target_tab and len(target_tab) > 50:
        return jsonify({'error': 'Target tab exceeds maximum length of 50 characters'}), 400
    if target_key and len(target_key) > 255:
        return jsonify({'error': 'Target key exceeds maximum length of 255 characters'}), 400

    result, error = create_comment(
        workspace_id=workspace_id,
        user_id=g.user_id,
        content=content,
        parent_id=parent_id,
        request_id=request_id,
        target_tab=target_tab,
        target_key=target_key
    )
    if error:
        if error == "Forbidden":
            return jsonify({'error': error}), 403
        if "not found" in error or "mismatch" in error:
            return jsonify({'error': error}), 400
        return jsonify({'error': error}), 400

    return jsonify(result), 201

@comment_bp.route('/api/comments/<int:comment_id>', methods=['PATCH'])
@token_required
def edit_comment_route(comment_id):
    data = request.json if request.is_json else {}
    content = data.get('content')

    if not content:
        return jsonify({'error': 'Content is required'}), 400
    if len(content) > 2000:
        return jsonify({'error': 'Content exceeds maximum length of 2000 characters'}), 400

    result, error = edit_comment(comment_id, g.user_id, content)
    if error:
        status = 403 if error == "Forbidden" else 404
        return jsonify({'error': error}), status
    return jsonify(result), 200

@comment_bp.route('/api/comments/<int:comment_id>', methods=['DELETE'])
@token_required
def delete_comment_route(comment_id):
    _, error = delete_comment(comment_id, g.user_id)
    if error:
        status = 403 if error == "Forbidden" else 404
        return jsonify({'error': error}), status
    return jsonify({'message': 'Comment deleted'}), 200
