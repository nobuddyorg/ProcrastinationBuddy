import requests
import streamlit as st
from config.constants import BACKEND_URL


def _handle_request_error(action: str, error: Exception):
    """Display a consistent error message."""
    st.error(f"Error {action} settings from {BACKEND_URL}: {error}")


def load_settings():
    """Fetch settings from the backend."""
    try:
        response = requests.get(f"{BACKEND_URL}/settings")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        _handle_request_error("loading", e)
        return None


def save_settings():
    """Send updated settings to the backend."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/settings", json=st.session_state.settings
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        _handle_request_error("saving", e)
        return False
