from unittest.mock import patch

import pytest
from flask import Flask

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
    with patch(
        "routes.tasks.get_model_status", return_value={"status": "ready"}
    ), patch("routes.tasks.generate_task", return_value="mock task") as mock_gen:
        response = client.post(
            "/tasks", json={"language": "german", "model": "fake-model"}
        )
        assert response.status_code == 201
        assert response.get_json() == {"task": "mock task"}
        mock_gen.assert_called_once()


def test_create_task_invalid_model(client):
    with patch("routes.tasks.generate_task") as mock_gen:
        response = client.post("/tasks", json={"model": "not a model!"})
        assert response.status_code == 400
        assert "error" in response.get_json()
        mock_gen.assert_not_called()


def test_create_task_model_not_ready(client):
    with patch(
        "routes.tasks.get_model_status",
        return_value={"status": "downloading", "completed": 1, "total": 10},
    ), patch("routes.tasks.ensure_model_pulling") as mock_pull, patch(
        "routes.tasks.generate_task"
    ) as mock_gen:
        response = client.post("/tasks", json={"model": "fake-model"})
        assert response.status_code == 409
        body = response.get_json()
        assert body["status"] == "downloading"
        mock_pull.assert_called_once()
        mock_gen.assert_not_called()


def test_create_task_failure(client):
    with patch(
        "routes.tasks.get_model_status", return_value={"status": "ready"}
    ), patch("routes.tasks.generate_task", side_effect=Exception("fail")):
        response = client.post("/tasks")
        assert response.status_code == 500
        assert "error" in response.get_json()


def test_model_status_endpoint(client):
    with patch(
        "routes.tasks.get_model_status", return_value={"status": "ready"}
    ) as mock_status:
        response = client.get("/models/status?model=fake-model")
        assert response.status_code == 200
        assert response.get_json() == {"status": "ready"}
        mock_status.assert_called_once()


def test_model_status_endpoint_invalid_model(client):
    response = client.get("/models/status?model=not a model!")
    assert response.status_code == 400


def test_pull_model_endpoint(client):
    with patch("routes.tasks.ensure_model_pulling") as mock_pull, patch(
        "routes.tasks.get_model_status", return_value={"status": "downloading"}
    ):
        response = client.post("/models/pull", json={"model": "fake-model"})
        assert response.status_code == 202
        assert response.get_json() == {"status": "downloading"}
        mock_pull.assert_called_once()


def test_pull_model_endpoint_invalid_model(client):
    with patch("routes.tasks.ensure_model_pulling") as mock_pull:
        response = client.post("/models/pull", json={"model": "not a model!"})
        assert response.status_code == 400
        mock_pull.assert_not_called()


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
