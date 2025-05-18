import pytest
from flask import Flask
from unittest.mock import patch
from routes.settings import settings_bp


@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(settings_bp)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_get_settings(client):
    mock_settings = {"theme": "dark"}

    with patch("routes.settings.get_settings") as mocked_get:
        mocked_get.return_value = type("obj", (object,), {"settings": mock_settings})()
        response = client.get("/settings")
        assert response.status_code == 200
        assert response.get_json() == mock_settings


def test_post_settings(client):
    with patch("routes.settings.save_settings") as mocked_save:
        response = client.post("/settings", json={"theme": "light"})
        mocked_save.assert_called_once_with({"theme": "light"})
        assert response.status_code == 200
        assert response.get_json() == {"message": "Settings saved"}
