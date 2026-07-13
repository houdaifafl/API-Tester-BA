from flask import Blueprint, jsonify, g, request as flask_request
from services.request_service import create_request, rename_request, delete_request, update_request_method, save_request
from services.jwt_service import token_required

request_bp = Blueprint('request', __name__)


@request_bp.route('/api/collections/<int:collection_id>/requests', methods=['POST'])
@token_required
def create_request_route(collection_id):
    result, error = create_request(collection_id, g.user_id)
    if error:
        status = 403 if error == 'Forbidden' else (404 if 'not found' in error else 400)
        return jsonify({'error': error}), status
    return jsonify(result), 201


@request_bp.route('/api/requests/<int:request_id>', methods=['PATCH'])
@token_required
def update_request_route(request_id):
    data = flask_request.json if flask_request.is_json else {}
    new_name = data.get('name')
    new_method = data.get('method')

    if new_name:
        if len(new_name) > 100:
            return jsonify({'error': 'Request name exceeds maximum length of 100 characters'}), 400
        result, error = rename_request(request_id, new_name, g.user_id)
        if error:
            status = 403 if error == 'Forbidden' else 404
            return jsonify({'error': error}), status
        return jsonify(result), 200

    if new_method:
        if len(new_method) > 10:
            return jsonify({'error': 'Request method exceeds maximum length of 10 characters'}), 400
        result, error = update_request_method(request_id, new_method, g.user_id)
        if error:
            status = 403 if error == 'Forbidden' else (400 if 'Invalid' in error else 404)
            return jsonify({'error': error}), status
        return jsonify(result), 200

    save_fields = {'url', 'params', 'headers', 'body', 'auth'}
    if save_fields & data.keys():
        url = data.get('url')
        if url and len(url) > 500:
            return jsonify({'error': 'URL exceeds maximum length of 500 characters'}), 400
        result, error = save_request(request_id, data, g.user_id)
        if error:
            status = 403 if error == 'Forbidden' else 404
            return jsonify({'error': error}), status
        return jsonify(result), 200

    return jsonify({'error': 'No valid fields provided'}), 400


@request_bp.route('/api/requests/<int:request_id>', methods=['DELETE'])
@token_required
def delete_request_route(request_id):
    _, error = delete_request(request_id, g.user_id)
    if error:
        status = 403 if error == 'Forbidden' else 404
        return jsonify({'error': error}), status
    return jsonify({'message': 'Request deleted'}), 200
