import pytest

from config import Config

Config.JWT_SECRET = "test-secret"

from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()
