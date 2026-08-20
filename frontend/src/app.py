import streamlit as st

from config.state import configure_states
from ui.page_setup import setup_custom_styles, setup_page
from ui.rendering import (
    render_header_elements,
    render_loading_spinner,
    render_model_download_progress,
    render_pagination,
    render_tasks,
)
from utils.models_api import sync_model_status
from utils.tasks_api import fetch_tasks


def main():
    configure_states()
    setup_page()
    setup_custom_styles()
    sync_model_status()
    render_header_elements()
    fetch_tasks()
    render_tasks(st.container())
    render_pagination()
    render_loading_spinner()
    render_model_download_progress()


if __name__ == "__main__":
    main()
