import requests
import streamlit as st
from datetime import datetime
from email.utils import parsedate_to_datetime
from config.constants import BACKEND_URL


def create_task():
    try:
        response = requests.post(
            f"{BACKEND_URL}/tasks",
            json={
                "language": st.session_state.settings["LANGUAGE"],
                "model": st.session_state.settings["MODEL"],
            },
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


def fetch_tasks():
    try:
        params = {
            "skip": (
                (st.session_state.page_number - 1)
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


def set_task_as_favorite(task, like=0):
    try:
        if task.get("favorite", 0) != like:
            requests.post(
                f"{BACKEND_URL}/tasks/{task['id']}/like",
                json={"like": like},
            )
    except requests.exceptions.RequestException as e:
        st.error(f"Error updating favorite status at {BACKEND_URL}: {e}")


def get_task_count(favorite=False):
    try:
        params = {"favorite": 1} if favorite else {}
        response = requests.get(f"{BACKEND_URL}/tasks/count", params=params)
        response.raise_for_status()
        return response.json().get("count", 0)
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching task count from {BACKEND_URL}: {e}")
        return 0


def delete_tasks():
    keep_favorites = 1 if st.session_state.keep_favorites else 0
    try:
        response = requests.delete(
            f"{BACKEND_URL}/tasks",
            params={"keep_favorites": keep_favorites},
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.error(f"Error deleting tasks from {BACKEND_URL}: {e}")
