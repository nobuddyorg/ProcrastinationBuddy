import requests
import streamlit as st
from config.constants import BACKEND_URL


def load_settings():
    try:
        response = requests.get(f"{BACKEND_URL}/settings")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error loading settings from {BACKEND_URL}: {e}")
        return None


def save_settings():
    try:
        response = requests.post(
            f"{BACKEND_URL}/settings", json=st.session_state.settings
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error saving settings to {BACKEND_URL}: {e}")
        return False
