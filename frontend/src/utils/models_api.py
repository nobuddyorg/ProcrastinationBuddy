import streamlit as st
from config.constants import BACKEND_URL
from utils.http import api_request


def sync_model_status():
    """Refresh readiness of the currently selected model and kick off a download if needed."""
    model = st.session_state.settings["MODEL"]
    status = get_model_status(model)

    if status is None:
        # Backend unreachable: don't lock the UI on a status we can't verify.
        st.session_state.model_ready = True
        st.session_state.model_download_status = None
        return

    st.session_state.model_download_status = status
    st.session_state.model_ready = status.get("status") == "ready"

    if status.get("status") == "not_downloaded":
        start_model_pull(model)


def get_model_status(model: str):
    """Fetch the readiness status of a model from the backend."""
    response = api_request(
        "get",
        f"{BACKEND_URL}/models/status",
        "checking model status",
        params={"model": model},
    )
    return response.json() if response is not None else None


def start_model_pull(model: str):
    """Ask the backend to start downloading a model."""
    response = api_request(
        "post",
        f"{BACKEND_URL}/models/pull",
        "starting model download",
        json={"model": model},
    )
    return response.json() if response is not None else None
