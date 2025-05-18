from unittest.mock import patch, MagicMock
from config.constants import BACKEND_URL
from utils.tasks_api import (
    create_task,
    fetch_tasks,
    set_task_as_favorite,
    get_task_count,
    delete_tasks,
)


mock_settings = {
    "LANGUAGE": "en",
    "MODEL": "gpt",
    "PAGE_SIZE": 2,
}


@patch("utils.tasks_api._get_setting", side_effect=lambda k: mock_settings[k])
@patch("utils.tasks_api.requests.post")
@patch("utils.tasks_api.st")
def test_create_task_success(mock_st, mock_post, mock_get_setting):
    mock_response = MagicMock()
    mock_response.json.return_value = {"task": '"Do something productive"'}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    result = create_task()

    assert result == "Do something productive"
    mock_post.assert_called_once()


@patch("utils.tasks_api._get_setting", side_effect=lambda k: mock_settings[k])
@patch("utils.tasks_api.requests.get")
@patch("utils.tasks_api.st")
def test_fetch_tasks_success(mock_st, mock_get, mock_get_setting):
    mock_st.session_state.page_number = 1
    mock_st.session_state.feedback_filter = False

    mock_get.return_value = MagicMock(
        json=lambda: [
            {
                "id": 1,
                "task_text": "Task A",
                "created_at": "Sun, 12 May 2024 10:00:00 GMT",
            },
            {
                "id": 2,
                "task_text": "Task B",
                "created_at": "Sun, 12 May 2024 11:00:00 GMT",
            },
        ],
        raise_for_status=lambda: None,
    )

    fetch_tasks()

    assert len(mock_st.session_state.task_list) == 2
    assert mock_st.session_state.task_list[0]["text"] == "Task B"  # Sorted newest first
    assert mock_get.called


@patch("utils.tasks_api.requests.post")
@patch("utils.tasks_api.st")
def test_set_task_as_favorite_changes_status(mock_st, mock_post):
    task = {"id": 123, "favorite": False}
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    set_task_as_favorite(task, like=1)

    mock_post.assert_called_once_with(f"{BACKEND_URL}/tasks/123/like", json={"like": 1})


@patch("utils.tasks_api.requests.post")
@patch("utils.tasks_api.st")
def test_set_task_as_favorite_no_change(mock_st, mock_post):
    task = {"id": 123, "favorite": 1}
    set_task_as_favorite(task, like=1)
    mock_post.assert_not_called()


@patch("utils.tasks_api.requests.get")
@patch("utils.tasks_api.st")
def test_get_task_count(mock_st, mock_get):
    mock_get.return_value = MagicMock(
        json=lambda: {"count": 42}, raise_for_status=lambda: None
    )

    count = get_task_count()
    assert count == 42
    mock_get.assert_called_once_with(f"{BACKEND_URL}/tasks/count", params={})


@patch("utils.tasks_api.requests.get")
@patch("utils.tasks_api.st")
def test_get_task_count_favorites(mock_st, mock_get):
    mock_get.return_value = MagicMock(
        json=lambda: {"count": 10}, raise_for_status=lambda: None
    )

    count = get_task_count(favorite=True)
    assert count == 10
    mock_get.assert_called_once_with(
        f"{BACKEND_URL}/tasks/count", params={"favorite": 1}
    )


@patch("utils.tasks_api.requests.delete")
@patch("utils.tasks_api.st")
def test_delete_tasks(mock_st, mock_delete):
    mock_st.session_state.keep_favorites = True

    mock_delete.return_value = MagicMock(raise_for_status=lambda: None)

    delete_tasks()
    mock_delete.assert_called_once_with(
        f"{BACKEND_URL}/tasks", params={"keep_favorites": 1}
    )
