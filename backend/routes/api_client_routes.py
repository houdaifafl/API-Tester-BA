from flask import Blueprint, request, jsonify
from backend.services.api_client_service import execute_request

api_client_bp = Blueprint("api_client", __name__)

@api_client_bp.route("/api/execute", methods=["POST"])
def handle_execute():
    data = request.json if request.is_json else {}

    # Extract data
    method = data.get("method") or request.args.get("method")
    url = data.get("url") or request.args.get("url")
    # Validation
    if not method or not url:
        return jsonify({"error": "Method and URL are required"}), 400

    method = method.upper()

    headers = data.get("headers")
    if not headers:
        allowed_headers = ["Authorization", "Content-Type"]
        headers = {
            key: value
            for key, value in request.headers.items()
            if key in allowed_headers
        }

    params = data.get("params")
    if not params:
        params = {
            key: value
            for key, value in request.args.items()
            if key not in ["method", "url"]
        }

    result = execute_request(method, url, params, headers)
    return result