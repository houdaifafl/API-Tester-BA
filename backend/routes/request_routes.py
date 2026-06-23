from flask import Blueprint, jsonify, request as flask_request
from services.request_service import create_request, rename_request, delete_request, update_request_method, save_request
from services.jwt_service import token_required

request_bp = Blueprint('request', __name__)


@request_bp.route('/api/collections/<int:collection_id>/requests', methods=['POST'])
@token_required
def create_request_route(collection_id):
    result, error = create_request(collection_id)
    if error:
        status = 404 if 'not found' in error else 400
        return jsonify({'error': error}), status
    return jsonify(result), 201


@request_bp.route('/api/requests/<int:request_id>', methods=['PATCH'])
@token_required
def update_request_route(request_id):
    data = flask_request.json if flask_request.is_json else {}
    new_name = data.get('name')
    new_method = data.get('method')

    if new_name:
        result, error = rename_request(request_id, new_name)
        if error:
            return jsonify({'error': error}), 404
        return jsonify(result), 200

    if new_method:
        result, error = update_request_method(request_id, new_method)
        if error:
            status = 400 if 'Invalid' in error else 404
            return jsonify({'error': error}), status
        return jsonify(result), 200

    save_fields = {'url', 'params', 'headers', 'body', 'auth'}
    if save_fields & data.keys():
        result, error = save_request(request_id, data)
        if error:
            return jsonify({'error': error}), 404
        return jsonify(result), 200

    return jsonify({'error': 'No valid fields provided'}), 400


@request_bp.route('/api/requests/<int:request_id>', methods=['DELETE'])
@token_required
def delete_request_route(request_id):
    _, error = delete_request(request_id)
    if error:
        return jsonify({'error': error}), 404
    return jsonify({'message': 'Request deleted'}), 200
