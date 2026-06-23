from flask import Blueprint, request, jsonify
from services.collection_service import (
    get_collections_by_workspace,
    add_collection,
    rename_collection,
    delete_collection,
)
from services.jwt_service import token_required

collection_bp = Blueprint('collection', __name__)


@collection_bp.route('/api/workspaces/<int:workspace_id>/collections', methods=['GET'])
@token_required
def list_collections(workspace_id):
    return jsonify(get_collections_by_workspace(workspace_id)), 200


@collection_bp.route('/api/workspaces/<int:workspace_id>/collections', methods=['POST'])
@token_required
def create_collection_route(workspace_id):
    result, error = add_collection(workspace_id)
    if error:
        return jsonify({'error': error}), 400
    return jsonify(result), 201


@collection_bp.route('/api/collections/<int:collection_id>', methods=['PATCH'])
@token_required
def rename_collection_route(collection_id):
    data = request.json if request.is_json else {}
    new_name = data.get('name')
    if not new_name:
        return jsonify({'error': 'name is required'}), 400
    result, error = rename_collection(collection_id, new_name)
    if error:
        return jsonify({'error': error}), 404
    return jsonify(result), 200


@collection_bp.route('/api/collections/<int:collection_id>', methods=['DELETE'])
@token_required
def delete_collection_route(collection_id):
    _, error = delete_collection(collection_id)
    if error:
        status = 403 if 'default' in error else 404
        return jsonify({'error': error}), status
    return jsonify({'message': 'Collection deleted'}), 200
