from flask import jsonify
import requests
import time

def execute_request(method, url, params=None, headers=None):
    try:
        start_time = time.time()
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            timeout=10
        )
        end_time = time.time()

        return jsonify({
            "status": response.status_code,
            "response_time": round((end_time - start_time) * 1000, 2),  # time in ms
            "data": response.json()
        })
    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timed out"}), 504

    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": str(e)}), 500  # 500: error from the server side


