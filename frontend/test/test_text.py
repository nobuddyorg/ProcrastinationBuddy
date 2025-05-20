from unittest.mock import patch
from utils.text import get_local_text, handle_request_error

mock_texts = {
    "en": {"greeting": "Hello"},
    "fr": {"greeting": "Bonjour"},
}


@patch("utils.text.TEXTS", mock_texts)
@patch("utils.text.st")
def test_get_local_text_returns_correct_language(mock_st):
    mock_st.session_state.settings = {"LANGUAGE": "fr"}
    result = get_local_text()
    assert result == {"greeting": "Bonjour"}

    mock_st.session_state.settings = {"LANGUAGE": "en"}
    result = get_local_text()
    assert result == {"greeting": "Hello"}


@patch("utils.text.BACKEND_URL", "http://localhost")
@patch("utils.text.st")
def test_handle_request_error_displays_error(mock_st):
    error = ValueError("Invalid request")
    handle_request_error("saving", error)
    mock_st.error.assert_called_once_with(
        "Error saving settings from http://localhost: Invalid request"
    )
