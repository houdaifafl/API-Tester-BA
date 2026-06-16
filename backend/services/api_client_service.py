from flask import jsonify
import requests
import time

def execute_request(method, url, params=None, headers=None, body=None):
    try:
        kwargs = {
            'method':  method,
            'url':     url,
            'headers': headers or {},
            'params':  params  or {},
            'timeout': 10,
        }

        if body is not None:
            if isinstance(body, (dict, list)):
                kwargs['json'] = body
            else:
                kwargs['data'] = str(body)

        start    = time.time()
        response = requests.request(**kwargs)
        elapsed  = round((time.time() - start) * 1000, 2)

        try:
            data = response.json()
        except ValueError:
            data = response.text

        return jsonify({
            'status':        response.status_code,
            'response_time': elapsed,
            'data':          data,
        })

    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timed out'}), 504

    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500
