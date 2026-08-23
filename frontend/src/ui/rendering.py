import streamlit as st

from utils.models_api import get_model_status
from utils.tasks_api import create_task, get_task_count, set_task_as_favorite
from utils.text import get_generic_text, get_local_text
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
            disabled=not st.session_state.get("model_ready", True),
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


def _render_button(key, label, rerun_on_click=False, disabled=False):
    if (
        st.button(
            label,
            disabled=st.session_state.running or disabled,
            key=key,
            use_container_width=True,
        )
        and rerun_on_click
    ):
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
        with (
            st.session_state.get("loading_spinner", st.container()),
            st.spinner(get_local_text()["main"]["spinner_text"]),
        ):
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


def render_model_download_progress():
    """Show model download progress, isolated in a fragment so only this
    section re-renders while downloading instead of the whole page."""
    if st.session_state.get("model_ready", True):
        return
    _poll_model_download()


@st.fragment(run_every=1)
def _poll_model_download():
    model = st.session_state.settings["MODEL"]
    status = get_model_status(model)
    if status is None:
        return

    st.session_state.model_download_status = status

    if status.get("status") == "ready":
        st.session_state.model_ready = True
        st.rerun()
        return

    local_text = get_local_text()["main"]

    if status.get("status") == "error":
        st.error(local_text["model_download_error"].format(model=model))
        return

    completed = status.get("completed", 0)
    total = status.get("total", 0)
    progress = min(completed / total, 1.0) if total else 0.0

    st.progress(
        progress, text=local_text["model_download_text"].format(model=model)
    )
