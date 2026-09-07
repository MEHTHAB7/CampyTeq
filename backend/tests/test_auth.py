import pytest
from rest_framework.test import APIClient
from colleges.models import College
from accounts.models import User

@pytest.mark.django_db
class TestAuthentication:
    def setup_method(self):
        self.client = APIClient()
        self.college = College.objects.create(
            name="Test Institute of Tech",
            code="TIT-TEST",
            slug="tit-test",
            status="ACTIVE"
        )
        self.user = User.objects.create_user(
            email="testuser@tit.edu",
            password="StrongPassword123!",
            first_name="Test",
            last_name="User",
            role="STUDENT",
            college=self.college,
            status="ACTIVE"
        )

    def test_login_success(self):
        response = self.client.post('/api/v1/auth/token/', {
            'email': 'testuser@tit.edu',
            'password': 'StrongPassword123!'
        })
        assert response.status_code == 200
        data = response.data
        assert 'access' in data
        assert 'refresh' in data
        assert 'user' in data
        assert data['user']['email'] == 'testuser@tit.edu'
        assert data['user']['role'] == 'STUDENT'
        assert data['user']['college']['code'] == 'TIT-TEST'

    def test_login_invalid_credentials(self):
        response = self.client.post('/api/v1/auth/token/', {
            'email': 'testuser@tit.edu',
            'password': 'WrongPassword!'
        })
        assert response.status_code == 401
        assert response.data.get('success') is False
        assert response.data.get('code') == 'UNAUTHENTICATED'

    def test_login_inactive_user_blocked(self):
        self.user.status = 'INACTIVE'
        self.user.save()
        response = self.client.post('/api/v1/auth/token/', {
            'email': 'testuser@tit.edu',
            'password': 'StrongPassword123!'
        })
        assert response.status_code in [400, 401]

    def test_token_refresh(self):
        login_res = self.client.post('/api/v1/auth/token/', {
            'email': 'testuser@tit.edu',
            'password': 'StrongPassword123!'
        })
        refresh_token = login_res.data['refresh']

        refresh_res = self.client.post('/api/v1/auth/token/refresh/', {
            'refresh': refresh_token
        })
        assert refresh_res.status_code == 200
        assert 'access' in refresh_res.data

    def test_get_current_user_profile(self):
        login_res = self.client.post('/api/v1/auth/token/', {
            'email': 'testuser@tit.edu',
            'password': 'StrongPassword123!'
        })
        token = login_res.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        profile_res = self.client.get('/api/v1/auth/me/')
        assert profile_res.status_code == 200
        assert profile_res.data['email'] == 'testuser@tit.edu'
