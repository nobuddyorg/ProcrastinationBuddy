import pytest
from unittest.mock import patch, MagicMock

from ui.rendering import (
    render_tasks,
    render_task,
    render_pagination,
    render_loading_spinner,
)


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
                "PAGE_SIZE": 5,
            },
            "feedback_filter": False,
            "page_number": 1,
            "running": False,
        }
    )
    monkeypatch.setattr("streamlit.session_state", session)
    return session


def test_render_tasks_shows_no_tasks_message(fake_session_state):
    fake_session_state["task_list"] = []
    container = MagicMock()

    with patch("ui.rendering.st") as mock_st:
        mock_st.session_state = fake_session_state
        render_tasks(container)

        mock_st.info.assert_called_once()


def test_render_tasks_renders_each_task(fake_session_state):
    fake_session_state["task_list"] = [
        {"id": 1, "text": "Task A", "time": "t1", "favorite": 0},
        {"id": 2, "text": "Task B", "time": "t2", "favorite": 0},
    ]
    container = MagicMock()

    with patch("ui.rendering.st") as mock_st, patch(
        "ui.rendering.render_task_and_feedback"
    ) as mock_render:
        mock_st.session_state = fake_session_state
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        render_tasks(container)

        assert mock_render.call_count == 2


def test_render_task_formats_timestamp_and_text():
    task = {"time": "2026-01-01T10:00:00Z", "text": "Do a thing"}

    with patch("ui.rendering.st") as mock_st, patch(
        "ui.rendering.format_time", return_value="10:00:00"
    ):
        render_task(task, "Europe/Berlin")

        mock_st.code.assert_called_once_with(
            "10:00:00: Do a thing", language="log", wrap_lines=True
        )


def test_render_pagination_hidden_for_single_page(fake_session_state):
    with patch("ui.rendering.st") as mock_st, patch(
        "ui.rendering.get_task_count", return_value=3
    ):
        mock_st.session_state = fake_session_state
        render_pagination()

        mock_st.pills.assert_not_called()


def test_render_pagination_computes_ceiling_page_count(fake_session_state):
    with patch("ui.rendering.st") as mock_st, patch(
        "ui.rendering.get_task_count", return_value=12
    ):
        mock_st.session_state = fake_session_state
        mock_st.pills.return_value = "1"
        render_pagination()

        # 12 tasks / page_size 5 -> 3 pages (ceiling division)
        assert mock_st.pills.call_args.kwargs["options"] == ["1", "2", "3"]


def test_render_pagination_updates_page_and_reruns_on_change(fake_session_state):
    with patch("ui.rendering.st") as mock_st, patch(
        "ui.rendering.get_task_count", return_value=12
    ):
        mock_st.session_state = fake_session_state
        mock_st.pills.return_value = "2"
        render_pagination()

        assert fake_session_state["page_number"] == 2
        mock_st.rerun.assert_called_once()


def test_render_loading_spinner_generates_task_when_running(fake_session_state):
    fake_session_state["running"] = True
    fake_session_state["loading_spinner"] = MagicMock()

    with patch("ui.rendering.st") as mock_st, patch(
        "ui.rendering.create_task"
    ) as mock_create_task:
        mock_st.session_state = fake_session_state
        render_loading_spinner()

        mock_create_task.assert_called_once()
        assert fake_session_state["running"] is False
        mock_st.rerun.assert_called_once()


def test_render_loading_spinner_noop_when_not_running(fake_session_state):
    fake_session_state["running"] = False

    with patch("ui.rendering.st") as mock_st, patch(
        "ui.rendering.create_task"
    ) as mock_create_task:
        mock_st.session_state = fake_session_state
        render_loading_spinner()

        mock_create_task.assert_not_called()
        mock_st.empty.assert_called_once()
