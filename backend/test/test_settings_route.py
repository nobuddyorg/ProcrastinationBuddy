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


VALID_SETTINGS = {
    "LANGUAGE": "English",
    "TIMEZONE": "Europe/London",
    "MODEL": "smollm2:1.7b",
    "PAGE_SIZE": 10,
}


def test_get_settings(client):
    mock_settings = {"theme": "dark"}

    with patch("routes.settings.get_settings") as mocked_get:
        mocked_get.return_value = type("obj", (object,), {"settings": mock_settings})()
        response = client.get("/settings")
        assert response.status_code == 200
        assert response.get_json() == mock_settings


def test_post_settings(client):
    with patch("routes.settings.save_settings") as mocked_save:
        response = client.post("/settings", json=VALID_SETTINGS)
        mocked_save.assert_called_once_with(VALID_SETTINGS)
        assert response.status_code == 200
        assert response.get_json() == {"message": "Settings saved"}


def test_post_settings_missing_field(client):
    incomplete = {k: v for k, v in VALID_SETTINGS.items() if k != "LANGUAGE"}
    with patch("routes.settings.save_settings") as mocked_save:
        response = client.post("/settings", json=incomplete)
        mocked_save.assert_not_called()
        assert response.status_code == 400
        assert "LANGUAGE" in response.get_json()["error"]


def test_post_settings_wrong_type(client):
    invalid = {**VALID_SETTINGS, "PAGE_SIZE": "ten"}
    with patch("routes.settings.save_settings") as mocked_save:
        response = client.post("/settings", json=invalid)
        mocked_save.assert_not_called()
        assert response.status_code == 400
