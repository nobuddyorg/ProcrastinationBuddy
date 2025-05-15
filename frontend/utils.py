import requests
import streamlit as st
import pytz
from datetime import datetime
from email.utils import parsedate_to_datetime
from constants import BACKEND_URL, SETTINGS, TEXTS


def generate_task():
    """Fetches a new task from the backend and inserts it into session state."""
    try:
        response = requests.get(
            f"{BACKEND_URL}/procrastinate?language={st.session_state.settings['LANGUAGE']}&model={SETTINGS['MODEL']}"
        )
        response.raise_for_status()
        task_text = response.json()["task"].strip('"')

        task_entry = {"text": task_text, "time": datetime.now().astimezone()}

        st.session_state.setdefault("task_list", []).insert(0, task_entry)
        st.session_state.task_list = st.session_state.task_list[
            : st.session_state.settings["PAGE_SIZE"]
        ]

        return task_text
    except requests.exceptions.RequestException as e:
        st.error(f"Error generating task from {BACKEND_URL}: {e}")
        return "Failed to get a task."


def handle_states():
    """Initializes states."""
    st.session_state.setdefault("running", False)
    st.session_state.setdefault("feedback_filter", False)
    st.session_state.setdefault("keep_favorites", True)

    backend_settings = load_settings()
    if backend_settings:
        st.session_state["settings"] = backend_settings
    else:
        st.session_state["settings"] = SETTINGS


def format_time(dt, timezone):
    """Returns formatted timestamp for display in user’s timezone."""
    try:
        tz = pytz.timezone(timezone)
        dt_local = dt.astimezone(tz)
        now = datetime.now(tz)
        return (
            dt_local.strftime("%H:%M:%S")
            if dt_local.date() == now.date()
            else dt_local.strftime("%Y-%m-%d %H:%M:%S")
        )
    except Exception:
        return dt.strftime("%Y-%m-%d %H:%M:%S")


def fetch_latest_tasks():
    """Fetches recent tasks from backend and stores them in session."""
    try:
        params = {
            "skip": (
                (st.session_state.settings["PAGE_NUMBER"] - 1)
                * st.session_state.settings["PAGE_SIZE"]
            ),
            "limit": st.session_state.settings["PAGE_SIZE"],
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
            key=lambda task: task["time"],
            reverse=True,
        )
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching tasks from {BACKEND_URL}: {e}")


def set_as_favorite(task, like=0):
    """Sets a task as favorite and stores in database."""
    try:
        if task.get("favorite", 0) != like:
            requests.post(
                f"{BACKEND_URL}/tasks/like",
                params={"task_id": task["id"], "like": like},
            )
    except requests.exceptions.RequestException as e:
        st.error(f"Error adding a like at {BACKEND_URL}: {e}")


def get_task_count(favorite=False):
    """Fetches the count of tasks from the backend."""
    try:
        params = {}
        if favorite:
            params["favorite"] = 1

        response = requests.get(f"{BACKEND_URL}/tasks/count", params=params)
        response.raise_for_status()
        return response.json().get("count", 0)
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching task count from {BACKEND_URL}: {e}")
        return 0


def delete_db():
    """Deletes all tasks from the database."""
    keep_favorites = 1 if st.session_state.keep_favorites else 0
    try:
        response = requests.delete(
            f"{BACKEND_URL}/tasks",
            params={"keep_favorites": keep_favorites},
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.error(f"Error deleting tasks from {BACKEND_URL}: {e}")


def load_settings():
    """Fetch app settings from backend."""
    try:
        response = requests.get(f"{BACKEND_URL}/settings")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error loading settings from {BACKEND_URL}: {e}")
        return None


def save_settings():
    """Save current settings to backend."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/settings", json=st.session_state.settings
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error saving settings to {BACKEND_URL}: {e}")
        return False


def get_local_text():
    """Returns the locale text based on the user's language setting."""
    return TEXTS[st.session_state.settings["LANGUAGE"]]
