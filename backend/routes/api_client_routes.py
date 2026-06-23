from flask import Blueprint, request, jsonify
from services.api_client_service import execute_request
from services.jwt_service import token_required

api_client_bp = Blueprint("api_client", __name__)

@api_client_bp.route("/api/execute", methods=["POST"])
@token_required
def handle_execute():
    data = request.json if request.is_json else {}

    method = data.get("method")
    url    = data.get("url")

    if not method or not url:
        return jsonify({"error": "Method and URL are required"}), 400

    headers = data.get("headers") or {}
    params  = data.get("params")  or {}
    body    = data.get("body")

    result = execute_request(method.upper(), url, params, headers, body)
    return result
