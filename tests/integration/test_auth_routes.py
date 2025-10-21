"""
Integration tests for authentication routes.
Tests for routes/auth.py endpoints.
"""

import json
from unittest.mock import patch


class TestAuthRoutes:
    """Test authentication route endpoints"""

    def test_login_invalid_json(self, client):
        """Test login with invalid JSON"""
        response = client.post(
            '/api/auth/login',
            data='invalid json',
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'Invalid JSON' in data['message']

    def test_login_exception_handling(self, client):
        """Test login exception handler"""
        with patch('routes.auth.security_manager.generate_token', side_effect=Exception('Test error')):
            login_data = {
                'username': 'admin',
                'password': 'admin123'
            }

            response = client.post(
                '/api/auth/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )

            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['status'] == 'error'

    def test_refresh_token_from_json(self, client):
        """Test refresh token endpoint with token in JSON body"""
        # First login to get tokens
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }

        login_response = client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )

        assert login_response.status_code == 200
        login_data = json.loads(login_response.data)
        refresh_token = login_data['data']['refresh_token']

        # Use refresh token from JSON body
        refresh_data = {'refresh_token': refresh_token}

        response = client.post(
            '/api/auth/refresh',
            data=json.dumps(refresh_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'access_token' in data['data']

    def test_refresh_token_from_header(self, client):
        """Test refresh token endpoint with token in Authorization header"""
        # First login to get tokens
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }

        login_response = client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )

        assert login_response.status_code == 200
        login_data = json.loads(login_response.data)
        refresh_token = login_data['data']['refresh_token']

        # Use refresh token from Authorization header
        response = client.post(
            '/api/auth/refresh',
            headers={'Authorization': f'Bearer {refresh_token}'},
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'

    def test_refresh_token_missing(self, client):
        """Test refresh token endpoint without token"""
        response = client.post(
            '/api/auth/refresh',
            data=json.dumps({}),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'Refresh token is required' in data['errors']

    def test_refresh_token_invalid(self, client):
        """Test refresh token endpoint with invalid token"""
        refresh_data = {'refresh_token': 'invalid_token_xyz'}

        response = client.post(
            '/api/auth/refresh',
            data=json.dumps(refresh_data),
            content_type='application/json'
        )

        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'Invalid refresh token' in data['message']

    def test_refresh_token_exception_handling(self, client):
        """Test refresh token exception handler"""
        with patch('routes.auth.security_manager.refresh_token', side_effect=Exception('Test error')):
            refresh_data = {'refresh_token': 'some_token'}

            response = client.post(
                '/api/auth/refresh',
                data=json.dumps(refresh_data),
                content_type='application/json'
            )

            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['status'] == 'error'

    def test_verify_token_success(self, client):
        """Test token verification success"""
        # First login to get token
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }

        login_response = client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )

        assert login_response.status_code == 200
        login_data = json.loads(login_response.data)
        access_token = login_data['data']['access_token']

        # Verify the token
        response = client.get(
            '/api/auth/verify',
            headers={'Authorization': f'Bearer {access_token}'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['valid'] is True
        assert 'user' in data['data']

    def test_verify_token_without_auth(self, client):
        """Test verify token without authentication header"""
        response = client.get('/api/auth/verify')

        # Should require authentication
        assert response.status_code == 401

    def test_logout_success(self, client):
        """Test successful logout"""
        # First login to get token
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }

        login_response = client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )

        assert login_response.status_code == 200
        login_data = json.loads(login_response.data)
        access_token = login_data['data']['access_token']

        # Logout
        response = client.post(
            '/api/auth/logout',
            headers={'Authorization': f'Bearer {access_token}'}
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'Logout successful' in data['message']

    def test_logout_exception_handling(self, client):
        """Test logout exception handler"""
        # First login to get token
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }

        login_response = client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )

        assert login_response.status_code == 200
        login_data = json.loads(login_response.data)
        access_token = login_data['data']['access_token']

        # Mock an exception during logout
        with patch('routes.auth.audit_logger.log_token_usage', side_effect=Exception('Test error')):
            response = client.post(
                '/api/auth/logout',
                headers={'Authorization': f'Bearer {access_token}'}
            )

            # Exception should be caught
            assert response.status_code in [200, 500]
