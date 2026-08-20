from unittest.mock import MagicMock, patch

import requests

from utils.http import api_request


@patch("utils.http.requests.get")
def test_api_request_returns_response_on_success(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = api_request("get", "http://example.test/thing", "doing a thing")

    assert result is mock_response
    mock_get.assert_called_once_with("http://example.test/thing")


@patch("utils.http.handle_request_error")
@patch(
    "utils.http.requests.post",
    side_effect=requests.exceptions.RequestException("boom"),
)
def test_api_request_returns_none_and_surfaces_error_on_failure(
    mock_post, mock_error_handler
):
    result = api_request("post", "http://example.test/thing", "doing a thing")

    assert result is None
    mock_error_handler.assert_called_once()
    assert mock_error_handler.call_args[0][0] == "doing a thing"


@patch("utils.http.requests.get")
def test_api_request_returns_none_on_http_error_status(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "500 Server Error"
    )
    mock_get.return_value = mock_response

    with patch("utils.http.handle_request_error") as mock_error_handler:
        result = api_request("get", "http://example.test/thing", "doing a thing")

    assert result is None
    mock_error_handler.assert_called_once()
