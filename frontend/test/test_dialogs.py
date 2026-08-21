import sys
from unittest.mock import MagicMock, patch

import pytest


def _passthrough_dialog(*args, **kwargs):
    def decorator(func):
        return func

    return decorator


@pytest.fixture
def dialogs_module():
    """ui.dialogs applies @st.dialog(...) at import time, so st.dialog must
    already be a passthrough decorator before the module is (re)imported."""
    with patch("streamlit.dialog", side_effect=_passthrough_dialog):
        sys.modules.pop("ui.dialogs", None)
        import ui.dialogs as module

        yield module
    sys.modules.pop("ui.dialogs", None)


@pytest.fixture
def fake_session_state(monkeypatch):
    class SessionState(dict):
        def __getattr__(self, key):
            return self[key]

        def __setattr__(self, key, value):
            self[key] = value

    session = SessionState(
        {
            "settings": {
                "LANGUAGE": "English",
                "TIMEZONE": "Europe/Berlin",
                "MODEL": "smollm2:1.7b",
                "PAGE_SIZE": 10,
            },
            "show_settings_dialog": False,
            "keep_favorites": True,
        }
    )
    monkeypatch.setattr("streamlit.session_state", session)
    return session


def test_render_select_setting_returns_selectbox_value(dialogs_module):
    with patch("ui.dialogs.st") as mock_st:
        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.selectbox.return_value = "chosen"

        result = dialogs_module._render_select_setting(
            label="Language",
            help_text="desc",
            options=["a", "b", "chosen"],
            current_value="a",
            key="lang",
        )

        assert result == "chosen"
        mock_st.selectbox.assert_called_once()


def test_save_button_updates_settings_and_reruns(dialogs_module, fake_session_state):
    with patch("ui.dialogs.st") as mock_st, patch(
        "ui.dialogs.save_settings"
    ) as mock_save, patch(
        "ui.dialogs._render_select_setting",
        side_effect=["Deutsch", "Europe/London", "mistral:instruct", "25"],
    ), patch("ui.dialogs._render_delete_controls"):
        mock_st.session_state = fake_session_state
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.button.return_value = True

        dialogs_module.show_settings_dialog()

        assert fake_session_state["settings"] == {
            "LANGUAGE": "Deutsch",
            "TIMEZONE": "Europe/London",
            "MODEL": "mistral:instruct",
            "PAGE_SIZE": 25,
        }
        mock_save.assert_called_once()
        mock_st.rerun.assert_called_once()


def test_wipe_db_button_deletes_tasks_and_reruns(dialogs_module, fake_session_state):
    with patch("ui.dialogs.st") as mock_st, patch(
        "ui.dialogs.delete_tasks"
    ) as mock_delete, patch("ui.dialogs.time.sleep"):
        mock_st.session_state = fake_session_state
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.button.return_value = True
        mock_st.checkbox.return_value = True

        dialogs_module._render_delete_controls(
            {
                "wipe_db": "Wipe",
                "wipe_db_desc": "desc",
                "keep_favorites": "Keep favorites",
            }
        )

        mock_delete.assert_called_once()
        assert fake_session_state["show_settings_dialog"] is True
        mock_st.rerun.assert_called_once()


def test_keep_favorites_checkbox_updates_session_state(
    dialogs_module, fake_session_state
):
    with patch("ui.dialogs.st") as mock_st:
        mock_st.session_state = fake_session_state
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.button.return_value = False
        mock_st.checkbox.return_value = False

        dialogs_module._render_delete_controls(
            {
                "wipe_db": "Wipe",
                "wipe_db_desc": "desc",
                "keep_favorites": "Keep favorites",
            }
        )

        assert fake_session_state["keep_favorites"] is False
