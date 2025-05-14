import requests
import streamlit as st
from streamlit_javascript import st_javascript
import pytz
from datetime import datetime
from email.utils import parsedate_to_datetime
from constants import BACKEND_URL


def generate_task():
    """Fetches a new task from the backend and inserts it into session state."""
    try:
        response = requests.get(f"{BACKEND_URL}/procrastinate")
        response.raise_for_status()
        task_text = response.json()["task"].strip('"')

        task_entry = {"text": task_text, "time": datetime.now().astimezone()}

        st.session_state.setdefault("task_list", []).insert(0, task_entry)
        st.session_state.task_list = st.session_state.task_list[:10]

        return task_text
    except requests.exceptions.RequestException as e:
        st.error(f"Error generating task from {BACKEND_URL}: {e}")
        return "Failed to get a task."


def handle_button_state():
    """Initializes button state."""
    st.session_state.setdefault("running", False)


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


def setup_timezone():
    """Sets up the user's timezone in session state."""
    if not st.session_state.get("timezone"):
        timezone = st_javascript("""await (async () => {
            const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            return userTimezone;
        })().then(returnValue => returnValue)""")
        if timezone:
            st.session_state["timezone"] = timezone


def fetch_latest_tasks():
    """Fetches recent tasks from backend and stores them in session."""
    try:
        response = requests.get(f"{BACKEND_URL}/tasks", params={"skip": 0, "limit": 10})
        response.raise_for_status()
        task_data = response.json()

        st.session_state["task_list"] = sorted(
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


def set_as_favorite(task_id, like=1):
    """Sets a task as favorite and stores in database."""
    requests.post(
        f"{BACKEND_URL}/tasks/like",
        params={"task_id": task_id, "like": like},
    )
