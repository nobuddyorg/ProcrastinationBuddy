from unittest.mock import patch, MagicMock
import requests

from utils.models_api import get_model_status, start_model_pull, sync_model_status


@patch("utils.models_api.BACKEND_URL", "http://localhost:8000")
@patch("utils.http.requests.get")
def test_get_model_status_success(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "ready"}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = get_model_status("some-model")

    assert result == {"status": "ready"}
    mock_get.assert_called_once_with(
        "http://localhost:8000/models/status", params={"model": "some-model"}
    )


@patch("utils.http.handle_request_error")
@patch(
    "utils.http.requests.get",
    side_effect=requests.exceptions.RequestException("Network error"),
)
def test_get_model_status_failure(mock_get, mock_error_handler):
    result = get_model_status("some-model")
    assert result is None
    mock_error_handler.assert_called_once()


@patch("utils.models_api.BACKEND_URL", "http://localhost:8000")
@patch("utils.http.requests.post")
def test_start_model_pull_success(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "downloading"}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    result = start_model_pull("some-model")

    assert result == {"status": "downloading"}
    mock_post.assert_called_once_with(
        "http://localhost:8000/models/pull", json={"model": "some-model"}
    )


@patch("utils.models_api.st")
@patch("utils.models_api.start_model_pull")
@patch("utils.models_api.get_model_status")
def test_sync_model_status_marks_ready(mock_status, mock_pull, mock_st):
    mock_st.session_state.settings = {"MODEL": "some-model"}
    mock_status.return_value = {"status": "ready"}

    sync_model_status()

    assert mock_st.session_state.model_ready is True
    assert mock_st.session_state.model_download_status == {"status": "ready"}
    mock_pull.assert_not_called()


@patch("utils.models_api.st")
@patch("utils.models_api.start_model_pull")
@patch("utils.models_api.get_model_status")
def test_sync_model_status_triggers_pull_when_not_downloaded(
    mock_status, mock_pull, mock_st
):
    mock_st.session_state.settings = {"MODEL": "some-model"}
    mock_status.return_value = {"status": "not_downloaded"}

    sync_model_status()

    assert mock_st.session_state.model_ready is False
    mock_pull.assert_called_once_with("some-model")


@patch("utils.models_api.st")
@patch("utils.models_api.start_model_pull")
@patch("utils.models_api.get_model_status")
def test_sync_model_status_fails_open_when_backend_unreachable(
    mock_status, mock_pull, mock_st
):
    mock_st.session_state.settings = {"MODEL": "some-model"}
    mock_status.return_value = None

    sync_model_status()

    assert mock_st.session_state.model_ready is True
    assert mock_st.session_state.model_download_status is None
    mock_pull.assert_not_called()
