import pytest
from app import create_app

class TestConfig:
    TESTING = True
    SECRET_KEY = 'test-key'

@pytest.fixture
def app():
    app = create_app(TestConfig)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_app_exists(app):
    assert app is not None

def test_app_is_testing(app):
    assert app.config['TESTING']

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
