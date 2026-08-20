import json
from unittest.mock import MagicMock, patch

import pytest

import services.tasks as tasks_module
from services.tasks import (
    ensure_model_pulling,
    generate_prompt,
    get_model_status,
    model_available,
)


@pytest.fixture(autouse=True)
def reset_pull_state():
    """_pull_state is memoized at module level; reset between tests."""
    original = tasks_module._pull_state
    tasks_module._pull_state = {}
    yield
    tasks_module._pull_state = original


def test_generate_prompt_contains_language_and_examples():
    lang = "french"
    prompt = generate_prompt(lang)

    assert f"Language (no translations): {lang}" in prompt
    assert "Examples of my favorites" in prompt
    assert "You are 'Procrastination Buddy'" in prompt
    assert prompt.count("\n") > 5


def test_model_available_true():
    mock_response = MagicMock()
    mock_response.json.return_value = {"models": [{"name": "smollm2:1.7b"}]}
    with patch("services.tasks.requests.get", return_value=mock_response):
        assert model_available("http://ollama", "smollm2:1.7b") is True


def test_model_available_false():
    mock_response = MagicMock()
    mock_response.json.return_value = {"models": [{"name": "other-model"}]}
    with patch("services.tasks.requests.get", return_value=mock_response):
        assert model_available("http://ollama", "smollm2:1.7b") is False


def test_get_model_status_ready_when_available():
    with patch("services.tasks.model_available", return_value=True):
        status = get_model_status("http://ollama", "smollm2:1.7b")
    assert status == {"status": "ready"}


def test_get_model_status_not_downloaded():
    with patch("services.tasks.model_available", return_value=False):
        status = get_model_status("http://ollama", "new-model")
    assert status == {"status": "not_downloaded"}


def test_get_model_status_reports_progress_while_downloading():
    tasks_module._set_pull_state(
        "new-model", status="downloading", detail="pulling", completed=5, total=10
    )
    status = get_model_status("http://ollama", "new-model")
    assert status == {
        "status": "downloading",
        "detail": "pulling",
        "completed": 5,
        "total": 10,
    }


def test_get_model_status_reports_error():
    tasks_module._set_pull_state("new-model", status="error", error="boom")
    status = get_model_status("http://ollama", "new-model")
    assert status == {"status": "error", "error": "boom"}


def test_ensure_model_pulling_skips_if_already_downloading():
    tasks_module._set_pull_state("new-model", status="downloading")
    with patch("services.tasks.threading.Thread") as mock_thread:
        ensure_model_pulling("http://ollama", "new-model")
    mock_thread.assert_not_called()


def test_ensure_model_pulling_skips_if_already_available():
    with patch("services.tasks.model_available", return_value=True), patch(
        "services.tasks.threading.Thread"
    ) as mock_thread:
        ensure_model_pulling("http://ollama", "new-model")
    mock_thread.assert_not_called()
    assert tasks_module._get_pull_state("new-model")["status"] == "ready"


def test_ensure_model_pulling_starts_background_thread():
    with patch("services.tasks.model_available", return_value=False), patch(
        "services.tasks.threading.Thread"
    ) as mock_thread:
        ensure_model_pulling("http://ollama", "new-model")
    mock_thread.assert_called_once()
    mock_thread.return_value.start.assert_called_once()


def test_run_pull_updates_progress_and_marks_ready():
    lines = [
        json.dumps({"status": "pulling manifest"}).encode(),
        json.dumps({"status": "pulling digest", "completed": 5, "total": 10}).encode(),
    ]
    mock_response = MagicMock()
    mock_response.iter_lines.return_value = lines
    mock_response.__enter__.return_value = mock_response
    mock_response.__exit__.return_value = False

    with patch("services.tasks.requests.post", return_value=mock_response):
        tasks_module._run_pull("http://ollama", "new-model")

    assert tasks_module._get_pull_state("new-model") == {
        "status": "ready",
        "detail": "pulling digest",
        "completed": 5,
        "total": 10,
    }


def test_run_pull_preserves_progress_on_trailing_messages_without_totals():
    """Ollama's final status lines (verifying/writing manifest) omit
    completed/total; the progress bar must not reset to 0 because of them."""
    lines = [
        json.dumps({"status": "pulling digest", "completed": 10, "total": 10}).encode(),
        json.dumps({"status": "verifying sha256 digest"}).encode(),
        json.dumps({"status": "writing manifest"}).encode(),
    ]
    mock_response = MagicMock()
    mock_response.iter_lines.return_value = lines
    mock_response.__enter__.return_value = mock_response
    mock_response.__exit__.return_value = False

    with patch("services.tasks.requests.post", return_value=mock_response):
        tasks_module._run_pull("http://ollama", "new-model")

    assert tasks_module._get_pull_state("new-model") == {
        "status": "ready",
        "detail": "writing manifest",
        "completed": 10,
        "total": 10,
    }


def test_run_pull_marks_error_on_failure():
    with patch("services.tasks.requests.post", side_effect=Exception("network down")):
        tasks_module._run_pull("http://ollama", "new-model")

    state = tasks_module._get_pull_state("new-model")
    assert state["status"] == "error"
    assert "network down" in state["error"]
