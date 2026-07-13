import pytest

class TestSecurityHeaders:

    def test_response_contains_security_headers(self, client):
        res = client.get('/')
        headers = res.headers

        # Content-Security-Policy
        assert 'Content-Security-Policy' in headers
        assert "default-src 'none'" in headers['Content-Security-Policy']

        # X-Content-Type-Options
        assert 'X-Content-Type-Options' in headers
        assert headers['X-Content-Type-Options'] == 'nosniff'

        # X-Frame-Options
        assert 'X-Frame-Options' in headers
        assert headers['X-Frame-Options'] == 'DENY'

        # Referrer-Policy
        assert 'Referrer-Policy' in headers
        assert headers['Referrer-Policy'] == 'no-referrer'

        # Strict-Transport-Security
        assert 'Strict-Transport-Security' in headers
        assert 'max-age=31536000' in headers['Strict-Transport-Security']

        # Permissions-Policy
        assert 'Permissions-Policy' in headers
        assert 'geolocation=()' in headers['Permissions-Policy']
