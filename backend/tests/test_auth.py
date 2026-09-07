"""Tests for JWT authentication endpoints."""
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
def test_obtain_jwt_token(client, admin_user):
    resp = client.post('/api/auth/login/', {
        'username': 'admin',
        'password': 'admin123456',
    }, format='json')
    assert resp.status_code == 200
    assert 'access' in resp.data
    assert 'refresh' in resp.data


@pytest.mark.django_db
def test_wrong_password_rejected(client, admin_user):
    resp = client.post('/api/auth/login/', {
        'username': 'admin',
        'password': 'wrong-password',
    }, format='json')
    assert resp.status_code == 401


@pytest.mark.django_db
def test_protected_endpoint_requires_auth(client):
    """Without token, dashboard stats returns 401."""
    resp = client.get('/api/dashboard/stats/')
    assert resp.status_code == 401


@pytest.mark.django_db
def test_refresh_token(client, admin_user):
    """Refresh endpoint accepts refresh token and returns new access."""
    token_resp = client.post('/api/auth/login/', {
        'username': 'admin',
        'password': 'admin123456',
    }, format='json')
    refresh = token_resp.data['refresh']

    resp = client.post('/api/auth/refresh/', {
        'refresh': refresh,
    }, format='json')
    assert resp.status_code == 200
    assert 'access' in resp.data


@pytest.mark.django_db
def test_authenticated_request(client, admin_user):
    """With token, request succeeds."""
    token_resp = client.post('/api/auth/login/', {
        'username': 'admin',
        'password': 'admin123456',
    }, format='json')
    access = token_resp.data['access']

    resp = client.get(
        '/api/dashboard/stats/',
        HTTP_AUTHORIZATION=f'Bearer {access}',
    )
    # 200 expected (empty tenant stats) — not 401
    assert resp.status_code == 200


@pytest.mark.django_db
def test_me_endpoint(client, admin_user):
    """GET /api/auth/me/ returns user info."""
    token_resp = client.post('/api/auth/login/', {
        'username': 'admin',
        'password': 'admin123456',
    }, format='json')
    access = token_resp.data['access']

    resp = client.get(
        '/api/auth/me/',
        HTTP_AUTHORIZATION=f'Bearer {access}',
    )
    assert resp.status_code == 200
    assert resp.data['username'] == 'admin'
    assert resp.data['role'] == 'super_admin'