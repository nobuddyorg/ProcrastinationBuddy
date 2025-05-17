import requests
import streamlit as st
from datetime import datetime
from email.utils import parsedate_to_datetime
from config.constants import BACKEND_URL


def _handle_request_error(action: str, error: Exception):
    st.error(f"Error {action} from {BACKEND_URL}: {error}")


def _get_setting(key: str):
    return st.session_state.settings.get(key)


def create_task():
    """Create a new task based on current language and model settings."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/tasks",
            json={
                "language": _get_setting("LANGUAGE"),
                "model": _get_setting("MODEL"),
            },
        )
        response.raise_for_status()
        task_text = response.json()["task"].strip('"')

        task_entry = {"text": task_text, "time": datetime.now().astimezone()}
        st.session_state.setdefault("task_list", []).insert(0, task_entry)

        page_size = _get_setting("PAGE_SIZE")
        st.session_state.task_list = st.session_state.task_list[:page_size]
        return task_text
    except requests.exceptions.RequestException as e:
        _handle_request_error("generating task", e)
        return "Failed to get a task."


def fetch_tasks():
    """Fetch a paginated list of tasks with optional filtering by favorite."""
    try:
        page = st.session_state.page_number
        page_size = _get_setting("PAGE_SIZE")
        params = {
            "skip": (page - 1) * page_size,
            "limit": page_size,
        }
        if st.session_state.feedback_filter:
            params["favorite"] = 1

        response = requests.get(f"{BACKEND_URL}/tasks", params=params)
        response.raise_for_status()

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
    except requests.exceptions.RequestException as e:
        _handle_request_error("fetching tasks", e)


def set_task_as_favorite(task, like=0):
    """Update the favorite status of a task."""
    try:
        if task.get("favorite", 0) != like:
            response = requests.post(
                f"{BACKEND_URL}/tasks/{task['id']}/like",
                json={"like": like},
            )
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        _handle_request_error("updating favorite status", e)


def get_task_count(favorite=False):
    """Return the count of tasks, optionally filtered by favorite status."""
    try:
        params = {"favorite": 1} if favorite else {}
        response = requests.get(f"{BACKEND_URL}/tasks/count", params=params)
        response.raise_for_status()
        return response.json().get("count", 0)
    except requests.exceptions.RequestException as e:
        _handle_request_error("fetching task count", e)
        return 0


def delete_tasks():
    """Delete all tasks, optionally preserving favorites."""
    try:
        keep_favorites = 1 if st.session_state.keep_favorites else 0
        response = requests.delete(
            f"{BACKEND_URL}/tasks", params={"keep_favorites": keep_favorites}
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        _handle_request_error("deleting tasks", e)
