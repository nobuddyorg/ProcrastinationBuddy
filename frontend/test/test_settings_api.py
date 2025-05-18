from unittest.mock import patch, MagicMock
import requests

from utils.settings_api import load_settings, save_settings


@patch("utils.settings_api.handle_request_error")
@patch(
    "utils.settings_api.requests.get",
    side_effect=requests.exceptions.RequestException("Network error"),
)
def test_load_settings_failure(mock_get, mock_error_handler):
    result = load_settings()
    assert result is None
    mock_error_handler.assert_called_once()
    assert mock_error_handler.call_args[0][0] == "loading"


@patch("utils.settings_api.BACKEND_URL", "http://localhost:8000")
@patch("utils.settings_api.requests.post")
@patch("utils.settings_api.st")
def test_save_settings_success(mock_st, mock_post):
    mock_st.session_state.settings = {"theme": "light"}

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    result = save_settings()
    assert result is True
    mock_post.assert_called_once_with(
        "http://localhost:8000/settings", json={"theme": "light"}
    )


@patch("utils.settings_api.handle_request_error")
@patch("utils.settings_api.st")
@patch(
    "utils.settings_api.requests.post",
    side_effect=requests.exceptions.RequestException("Server error"),
)
def test_save_settings_failure(mock_post, mock_st, mock_error_handler):
    mock_st.session_state.settings = {"theme": "dark"}

    result = save_settings()
    assert result is False
    mock_error_handler.assert_called_once()
    assert mock_error_handler.call_args[0][0] == "saving"
