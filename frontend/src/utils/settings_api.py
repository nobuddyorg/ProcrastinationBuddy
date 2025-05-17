import requests
import streamlit as st
from config.constants import BACKEND_URL
from utils.text import handle_request_error


def load_settings():
    """Fetch settings from the backend."""
    try:
        response = requests.get(f"{BACKEND_URL}/settings")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        handle_request_error("loading", e)
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
        handle_request_error("saving", e)
        return False
