from flask import Blueprint, request, jsonify
from backend.services.collection_service import create_collection

collection_bp = Blueprint('collection', __name__)

@collection_bp.route('/api/collections', methods=['POST'])
def create_collection_route():
    data = request.json if request.is_json else {}
    name = data.get("name")

    # Validation
    if not name:
        return jsonify({"error": "Collection name is required"}), 400

    result = create_collection(name)
    return jsonify(result), 201
