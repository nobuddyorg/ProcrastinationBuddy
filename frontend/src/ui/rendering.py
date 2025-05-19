import streamlit as st
from utils.tasks_api import create_task, set_task_as_favorite, get_task_count
from utils.text import get_local_text, get_generic_text
from utils.time import format_time


def render_header_elements():
    """Render header buttons, filter toggle, and loading spinner container."""
    local_text = get_local_text()

    col1, col2, col3, col4, col5 = st.columns(
        [0.15, 0.1, 0.1, 0.19, 0.46], border=False
    )

    with col1:
        _render_button(
            "generate_button",
            local_text["main"]["generate_button"],
            rerun_on_click=True,
        )

    with col2:
        _render_dialog_button(
            get_generic_text()["info_button"], "ui.dialogs", "show_help_dialog"
        )

    with col3:
        _render_dialog_button(
            get_generic_text()["config_button"], "ui.dialogs", "show_settings_dialog"
        )

    with col4:
        _render_feedback_filter_toggle()

    with col5:
        st.session_state.loading_spinner = st.container()


def _render_button(key, label, rerun_on_click=False):
    if st.button(
        label, disabled=st.session_state.running, key=key, use_container_width=True
    ):
        if rerun_on_click:
            st.session_state.running = True
            st.rerun()


def _render_dialog_button(label, module_path, function_name):
    if st.button(
        label, disabled=st.session_state.running, use_container_width=True
    ) or st.session_state.get(function_name, False):
        st.session_state[function_name] = True
        module = __import__(module_path, fromlist=[function_name])
        getattr(module, function_name)()


def _render_feedback_filter_toggle():
    on = st.toggle(
        "Filter Likes", key="feedback_filter_toggle", disabled=st.session_state.running
    )
    if on != st.session_state.feedback_filter:
        st.session_state.feedback_filter = on
        if on:
            st.session_state.old_page_number = st.session_state.page_number
            st.session_state.page_number = 1
        else:
            st.session_state.page_number = st.session_state.old_page_number


def render_feedback(idx, task):
    """Render the feedback (like) pill UI."""
    options = [get_generic_text()["like_button"]]
    selected = st.pills(
        label="feedback selection",
        options=options,
        selection_mode="single",
        key=f"feedback_{task.get('id')}_{-idx}",
        label_visibility="collapsed",
        default=options[0] if task.get("favorite", 0) else None,
        disabled=st.session_state.running,
    )
    set_task_as_favorite(task, like=1 if selected else 0)


def render_task(task, timezone):
    """Render a single task code block."""
    timestamp = format_time(task["time"], timezone)
    st.code(f"{timestamp}: {task['text']}", language="log", wrap_lines=True)


def render_tasks(container):
    """Render all tasks with alternating layout."""
    timezone = st.session_state.settings["TIMEZONE"]
    task_list = st.session_state.get("task_list", [])

    with container:
        if not task_list:
            st.info(get_local_text()["main"]["no_tasks_text"])
            return

        for idx, task in enumerate(task_list):
            is_even = idx % 2 == 0
            cols = st.columns([0.88, 0.1, 0.02] if is_even else [0.02, 0.88, 0.1])
            render_task_and_feedback(cols, task, idx, timezone, is_even)


def render_task_and_feedback(cols, task, idx, timezone, is_even):
    left, middle, right = cols
    with left:
        render_task(task, timezone) if is_even else st.empty()
    with middle:
        render_feedback(idx, task) if is_even else render_task(task, timezone)
    with right:
        st.empty() if is_even else render_feedback(idx, task)


def render_loading_spinner():
    """Render loading spinner if generation is in progress."""
    if st.session_state.running:
        with st.session_state.get("loading_spinner", st.container()):
            with st.spinner(get_local_text()["main"]["spinner_text"]):
                create_task()
                st.session_state.running = False
                st.rerun()
    else:
        st.empty()


def render_pagination():
    """Render page navigation pills."""
    page_size = st.session_state.settings["PAGE_SIZE"]
    total_tasks = get_task_count(st.session_state.feedback_filter)
    total_pages = (total_tasks + page_size - 1) // page_size  # correct ceiling division

    if total_pages <= 1:
        return

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

    if selection and int(selection) != current_page:
        st.session_state.page_number = int(selection)
        st.rerun()
