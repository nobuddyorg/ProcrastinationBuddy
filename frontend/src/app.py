import streamlit as st
from ui.rendering import (
    render_header_elements,
    render_tasks,
    render_loading_spinner,
    render_pagination,
)
from ui.page_setup import setup_page, setup_custom_styles
from config.state import configure_states
from utils.tasks_api import fetch_tasks


def main():
    configure_states()
    setup_page()
    setup_custom_styles()
    render_header_elements()
    fetch_tasks()
    render_tasks(st.container())
    render_pagination()
    render_loading_spinner()


if __name__ == "__main__":
    main()
