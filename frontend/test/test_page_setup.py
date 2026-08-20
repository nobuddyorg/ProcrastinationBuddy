from unittest.mock import patch

import pytest

from config.constants import LAYOUT, PAGE_ICON
from ui.page_setup import setup_custom_styles, setup_page


@pytest.fixture
def fake_session_state(monkeypatch):
    class SessionState(dict):
        def __getattr__(self, key):
            return self[key]

        def __setattr__(self, key, value):
            self[key] = value

    session = SessionState({"settings": {"LANGUAGE": "English"}})
    monkeypatch.setattr("streamlit.session_state", session)
    return session


def test_setup_page_uses_page_config_and_language_subtitle(fake_session_state):
    with patch("ui.page_setup.st") as mock_st:
        mock_st.session_state = fake_session_state
        setup_page()

        mock_st.set_page_config.assert_called_once_with(
            page_title="Procrastination Buddy ⏰🤷",
            page_icon=PAGE_ICON,
            layout=LAYOUT,
        )
        mock_st.title.assert_called_once_with("Procrastination Buddy ⏰🤷")

        markdown_html = mock_st.markdown.call_args[0][0]
        assert "Your partner in crime for finding perfectly pointless tasks!" in (
            markdown_html
        )
        assert mock_st.markdown.call_args.kwargs["unsafe_allow_html"] is True


def test_setup_page_uses_current_language(fake_session_state):
    fake_session_state["settings"] = {"LANGUAGE": "Deutsch"}
    with patch("ui.page_setup.st") as mock_st:
        mock_st.session_state = fake_session_state
        setup_page()

        markdown_html = mock_st.markdown.call_args[0][0]
        assert "Dein Komplize bei der Suche nach völlig sinnlosen Aufgaben!" in (
            markdown_html
        )


def test_setup_custom_styles_injects_css():
    with patch("ui.page_setup.st") as mock_st:
        setup_custom_styles()

        mock_st.markdown.assert_called_once()
        css = mock_st.markdown.call_args[0][0]
        assert "<style>" in css
        assert mock_st.markdown.call_args.kwargs["unsafe_allow_html"] is True
