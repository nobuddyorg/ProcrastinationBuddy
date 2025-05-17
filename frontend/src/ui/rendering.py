import streamlit as st
from utils.tasks_api import (
    create_task,
    set_task_as_favorite,
    get_task_count,
)

from utils.text import get_local_text
from utils.time import format_time


def render_header_elements():
    """Renders the header elements including buttons and loading spinner."""
    local_text = get_local_text()

    col1, col2, col3, col4, col5 = st.columns(
        [0.15, 0.1, 0.1, 0.19, 0.46], border=False
    )

    with col1:
        if st.button(
            local_text["main"]["generate_button"],
            disabled=st.session_state.running,
            key="generate_button",
            use_container_width=True,
        ):
            st.session_state.running = True
            st.rerun()

    with col2:
        if st.button(
            local_text["main"]["info_button"],
            disabled=st.session_state.running,
            use_container_width=True,
        ):
            from dialogs import show_help_dialog

            show_help_dialog()

    with col3:
        if st.button(
            local_text["main"]["config_button"],
            disabled=st.session_state.running,
            use_container_width=True,
        ):
            from dialogs import show_settings_dialog

            show_settings_dialog()

    with col4:
        on = st.toggle(
            "Filter Likes",
            key="feedback_filter_toggle",
            disabled=st.session_state.running,
        )
        if (on and not st.session_state.feedback_filter) or (
            not on and st.session_state.feedback_filter
        ):
            st.session_state.feedback_filter = True if on else False
            st.session_state.page_number = 1

    with col5:
        st.session_state.loading_spinner = st.container()


def render_feedback(idx, task):
    """Renders feedback pill UI for a task."""
    options = [get_local_text()["main"]["like_button"]]
    selection = st.pills(
        label="feedback selection",
        options=options,
        selection_mode="single",
        key=f"feedback_{task.get('id'), -idx}",
        label_visibility="collapsed",
        default=options[0] if task.get("favorite", 0) else None,
        disabled=st.session_state.running,
    )
    set_task_as_favorite(task, like=1 if selection else 0)


def render_task(task, timezone):
    """Renders a single task box with styling."""
    st.code(
        f"{format_time(task['time'], timezone)}: {task['text']}",
        language="log",
        wrap_lines=True,
    )


def render_tasks(container):
    """Displays tasks with alternating layout."""
    timezone = st.session_state.settings["TIMEZONE"]
    with container:
        task_list = st.session_state.get("task_list", [])
        if not task_list:
            st.info(get_local_text()["main"]["no_tasks_text"])
            return

        for idx, task in enumerate(task_list):
            if idx % 2 == 0:
                left, middle, right = st.columns([0.88, 0.1, 0.02])
            else:
                left, middle, right = st.columns([0.02, 0.88, 0.1])

            with left:
                if idx % 2 == 0:
                    render_task(task, timezone)
                else:
                    st.empty()

            with middle:
                if idx % 2 == 0:
                    render_feedback(idx, task)
                else:
                    render_task(task, timezone)

            with right:
                if idx % 2 == 0:
                    st.empty()
                else:
                    render_feedback(idx, task)


def render_loading_spinner():
    """Displays a loading spinner while generating tasks."""
    if st.session_state.running:
        with st.session_state.get("loading_spinner", st.container()):
            with st.spinner(get_local_text()["main"]["spinner_text"]):
                create_task()
                st.session_state.running = False
                st.rerun()
    else:
        st.empty()


def render_pagination():
    total_tasks = get_task_count(st.session_state.feedback_filter)
    total_pages = (total_tasks // (st.session_state.settings["PAGE_SIZE"] + 1)) + 1
    if total_pages > 1:
        current_page = st.session_state.page_number

        options = [str(i) for i in range(1, total_pages + 1)]

        selection = st.pills(
            label="page selection",
            options=options,
            selection_mode="single",
            key="page_selection",
            label_visibility="collapsed",
            default=str(current_page) if str(current_page) in options else options[0],
            disabled=st.session_state.running,
        )

        if selection is not None and int(selection) != current_page:
            st.session_state.page_number = int(selection)
            st.rerun()
