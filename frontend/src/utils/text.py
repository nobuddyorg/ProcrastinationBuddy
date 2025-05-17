import streamlit as st
from config.constants import TEXTS, BACKEND_URL


def get_local_text():
    return TEXTS[st.session_state.settings["LANGUAGE"]]


def handle_request_error(action: str, error: Exception):
    """Display a consistent error message."""
    st.error(f"Error {action} settings from {BACKEND_URL}: {error}")
