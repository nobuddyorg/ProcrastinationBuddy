import pytest
from unittest.mock import patch

from config.constants import SETTINGS
from config.state import configure_states


@pytest.fixture
def fake_session_state(monkeypatch):
    class SessionState(dict):
        def __getattr__(self, key):
            return self[key]

        def __setattr__(self, key, value):
            self[key] = value

    session = SessionState()
    monkeypatch.setattr("streamlit.session_state", session)
    return session


def test_configure_states_with_backend_settings(fake_session_state):
    backend_settings = {"theme": "dark"}

    with patch("config.state.load_settings", return_value=backend_settings):
        configure_states()

    assert fake_session_state["running"] is False
    assert fake_session_state["feedback_filter"] is False
    assert fake_session_state["keep_favorites"] is True
    assert fake_session_state["page_number"] == 1
    assert fake_session_state["old_page_number"] == 1
    assert fake_session_state["settings"] == backend_settings


def test_configure_states_with_no_backend_settings(fake_session_state):
    with patch("config.state.load_settings", return_value=None):
        configure_states()

    assert fake_session_state["settings"] == SETTINGS
