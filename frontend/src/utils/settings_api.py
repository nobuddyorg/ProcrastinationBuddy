import streamlit as st

from config.constants import BACKEND_URL
from utils.http import api_request


def load_settings():
    """Fetch settings from the backend."""
    response = api_request("get", f"{BACKEND_URL}/settings", "loading")
    return response.json() if response is not None else None


def save_settings():
    """Send updated settings to the backend."""
    response = api_request(
        "post", f"{BACKEND_URL}/settings", "saving", json=st.session_state.settings
    )
    return response is not None
