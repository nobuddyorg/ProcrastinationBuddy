import pytest
from flask import Flask
from unittest.mock import patch
from routes.tasks import tasks_bp


@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(tasks_bp)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_create_task_success(client):
    with patch("routes.tasks.generate_task", return_value="mock task") as mock_gen:
        response = client.post(
            "/tasks", json={"language": "german", "model": "fake-model"}
        )
        assert response.status_code == 201
        assert response.get_json() == {"task": "mock task"}
        mock_gen.assert_called_once()


def test_create_task_failure(client):
    with patch("routes.tasks.generate_task", side_effect=Exception("fail")):
        response = client.post("/tasks")
        assert response.status_code == 500
        assert "error" in response.get_json()


def test_get_tasks(client):
    with patch(
        "routes.tasks.list_tasks", return_value=[{"id": 1, "task_text": "test"}]
    ):
        response = client.get("/tasks?skip=0&limit=5")
        assert response.status_code == 200
        assert isinstance(response.get_json(), list)


def test_get_task_count(client):
    with patch("routes.tasks.count_tasks", return_value=42):
        response = client.get("/tasks/count")
        assert response.status_code == 200
        assert response.get_json() == {"count": 42}


def test_update_like_valid(client):
    with patch("routes.tasks.like_task") as mock_like:
        response = client.post("/tasks/1/like", json={"like": 1})
        assert response.status_code == 200
        mock_like.assert_called_once_with(1, 1)


def test_update_like_invalid(client):
    response = client.post("/tasks/1/like", json={"like": 3})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_delete_tasks(client):
    with patch("routes.tasks.delete_all_tasks") as mock_delete:
        response = client.delete("/tasks?keep_favorites=0")
        assert response.status_code == 200
        mock_delete.assert_called_once_with(keep_favorites=False)
