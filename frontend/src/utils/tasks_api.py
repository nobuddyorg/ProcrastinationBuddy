import streamlit as st
from datetime import datetime
from email.utils import parsedate_to_datetime
from config.constants import BACKEND_URL
from utils.http import api_request


def _get_setting(key: str):
    return st.session_state.settings.get(key)


def create_task():
    """Create a new task based on current language and model settings."""
    response = api_request(
        "post",
        f"{BACKEND_URL}/tasks",
        "generating task",
        json={
            "language": _get_setting("LANGUAGE"),
            "model": _get_setting("MODEL"),
        },
    )
    if response is None:
        return "Failed to get a task."

    task_text = response.json()["task"].strip('"')

    task_entry = {"text": task_text, "time": datetime.now().astimezone()}
    st.session_state.setdefault("task_list", []).insert(0, task_entry)

    page_size = _get_setting("PAGE_SIZE")
    st.session_state.task_list = st.session_state.task_list[:page_size]
    return task_text


def fetch_tasks():
    """Fetch a paginated list of tasks with optional filtering by favorite."""
    page = st.session_state.page_number
    page_size = _get_setting("PAGE_SIZE")
    params = {
        "skip": (page - 1) * page_size,
        "limit": page_size,
    }
    if st.session_state.feedback_filter:
        params["favorite"] = 1

    response = api_request(
        "get", f"{BACKEND_URL}/tasks", "fetching tasks", params=params
    )
    if response is None:
        return

    task_data = response.json()
    st.session_state.task_list = sorted(
        [
            {
                "id": task["id"],
                "text": task["task_text"],
                "time": parsedate_to_datetime(task["created_at"]),
                "favorite": task.get("favorite", False),
            }
            for task in task_data
        ],
        key=lambda t: t["time"],
        reverse=True,
    )


def set_task_as_favorite(task, like=0):
    """Update the favorite status of a task."""
    if task.get("favorite", 0) != like:
        api_request(
            "post",
            f"{BACKEND_URL}/tasks/{task['id']}/like",
            "updating favorite status",
            json={"like": like},
        )


def get_task_count(favorite=False):
    """Return the count of tasks, optionally filtered by favorite status."""
    params = {"favorite": 1} if favorite else {}
    response = api_request(
        "get", f"{BACKEND_URL}/tasks/count", "fetching task count", params=params
    )
    return response.json().get("count", 0) if response is not None else 0


def delete_tasks():
    """Delete all tasks, optionally preserving favorites."""
    keep_favorites = 1 if st.session_state.keep_favorites else 0
    api_request(
        "delete",
        f"{BACKEND_URL}/tasks",
        "deleting tasks",
        params={"keep_favorites": keep_favorites},
    )
