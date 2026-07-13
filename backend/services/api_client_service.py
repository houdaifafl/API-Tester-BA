from flask import jsonify
import requests
import time
import ipaddress
import socket
from urllib.parse import urlparse

# ── SSRF Protection ────────────────────────────────────────────────────────────
# All IP ranges that must never be reachable via the /api/execute proxy.
_BLOCKED_NETWORKS = [
    # Loopback
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("::1/128"),
    # Private / RFC-1918
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    # Link-local (also covers cloud metadata: 169.254.169.254)
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("fe80::/10"),
    # Unique local (IPv6 private)
    ipaddress.ip_network("fc00::/7"),
    # Multicast
    ipaddress.ip_network("224.0.0.0/4"),
    ipaddress.ip_network("ff00::/8"),
    # Unspecified / broadcast
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("::/128"),
]

_ALLOWED_SCHEMES = {"http", "https"}


def _is_ssrf_safe(url):
    """
    Returns (True, None) when the URL is safe to proxy.
    Returns (False, reason_string) when it must be rejected.

    Checks performed:
    1. URL must be parseable and have a non-empty hostname.
    2. Scheme must be http or https.
    3. Resolved IP must not fall in any private/internal network.
    """
    try:
        parsed = urlparse(url)
    except Exception:
        return False, "Invalid URL"

    if not parsed.hostname:
        return False, "URL must contain a valid hostname"

    if parsed.scheme.lower() not in _ALLOWED_SCHEMES:
        return False, f"URL scheme '{parsed.scheme}' is not allowed. Use http or https."

    # Resolve hostname → IP (catches DNS rebinding at the moment of the check)
    try:
        resolved_ip = socket.getaddrinfo(parsed.hostname, None, socket.AF_UNSPEC)[0][4][0]
        ip_obj = ipaddress.ip_address(resolved_ip)
    except socket.gaierror:
        return False, f"Could not resolve hostname '{parsed.hostname}'"
    except ValueError:
        return False, "Resolved address is not a valid IP"

    for network in _BLOCKED_NETWORKS:
        if ip_obj in network:
            return False, (
                f"Requests to internal or private addresses are not allowed "
                f"(resolved to {resolved_ip})"
            )

    return True, None


# ── Request Executor ───────────────────────────────────────────────────────────

def execute_request(method, url, params=None, headers=None, body=None):
    # SSRF guard — must pass before any network I/O
    safe, reason = _is_ssrf_safe(url)
    if not safe:
        return jsonify({'error': f'Blocked request: {reason}'}), 400

    try:
        kwargs = {
            'method':  method,
            'url':     url,
            'headers': headers or {},
            'params':  params  or {},
            'timeout': 10,
            # Disable automatic redirects to private IPs after an open redirect
            'allow_redirects': False,
        }

        if body is not None:
            if isinstance(body, (dict, list)):
                kwargs['json'] = body
            else:
                kwargs['data'] = str(body)

        start    = time.time()
        response = requests.request(**kwargs)
        elapsed  = round((time.time() - start) * 1000, 2)

        # If the server issued a redirect, validate the redirect destination too
        if response.status_code in (301, 302, 303, 307, 308):
            location = response.headers.get('Location', '')
            redir_safe, redir_reason = _is_ssrf_safe(location)
            if not redir_safe:
                return jsonify({'error': f'Blocked redirect: {redir_reason}'}), 400
            # Follow the validated redirect manually
            kwargs['url'] = location
            kwargs['method'] = 'GET'
            response = requests.request(**kwargs)
            elapsed = round((time.time() - start) * 1000, 2)

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
