import time
import streamlit as st
import pytz
from utils.constants import TEXTS, PAGE_ICON, LAYOUT, MODELS
from utils.utils import (
    generate_task,
    handle_states,
    format_time,
    fetch_latest_tasks,
    set_as_favorite,
    get_task_count,
    get_local_text,
    delete_db,
    save_settings,
)


def setup_page():
    """Sets up the Streamlit page configuration."""
    st.set_page_config(
        page_title=TEXTS["generic"]["title"],
        page_icon=PAGE_ICON,
        layout=LAYOUT,
    )
    st.title(TEXTS["generic"]["title"])
    st.markdown(
        f"<h5 style='margin-top: -20px; font-size: 16px; font-style: italic;'>{TEXTS[st.session_state.settings['LANGUAGE']]['main']['subtitle']}</h5>",
        unsafe_allow_html=True,
    )


def setup_custom_styles():
    """Applies custom CSS styles to the Streamlit app."""
    st.markdown(
        """
        <style>
        pre {
            margin-bottom: -0.3rem !important;
        }
        .stApp .row-widget.stColumns {
            column-gap: 0rem !important;
        }
        .stApp .stColumn {
            padding: 0 !important;
            margin: 0 !important;
        }
        .stSpinner > div {
            margin-top: 0.45rem !important;
        }
        [data-testid="stBaseButton-pills"],
        [data-testid="stBaseButton-pillsActive"] {
            margin-top: 0.3rem !important;
            margin-bottom: -0.3rem !important;
        }
        #MainMenu, footer, header {
            visibility: hidden !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


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
            show_help_dialog()

    with col3:
        if st.button(
            local_text["main"]["config_button"],
            disabled=st.session_state.running,
            use_container_width=True,
        ):
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

    set_as_favorite(task, like=1 if selection else 0)


def render_task(task, timezone):
    """Renders a single task box with styling."""
    st.code(
        f"{format_time(task['time'], timezone)}: {task['text']}",
        language="log",
        wrap_lines=True,
    )


def render_tasks(container):
    """Displays up to PAGE_SIZE tasks with alternating layout and theme-based styling."""
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
                generate_task()
                st.session_state.running = False
                st.rerun()
    else:
        st.empty()


@st.dialog(TEXTS["generic"]["help_dialog"], width="large")
def show_help_dialog():
    """Displays the sarcastic help/about dialog."""
    local_text = get_local_text()["help"]

    st.markdown(f"<h1>{local_text['title']}</h1>", unsafe_allow_html=True)
    st.write(local_text["intro"])
    st.write(local_text["middle"])

    col1, col2 = st.columns(2)

    with col1:
        st.write(local_text["pomodoro_title"])
        st.write(local_text["pomodoro_desc"])
        st.image("/app/src/ui/img/pomodoro.png", caption="Pomodoro Technique, Wikipedia", width=250)
        st.markdown(
            f"[{local_text['pomodoro_link']}](https://en.wikipedia.org/wiki/Pomodoro_Technique)"
        )

    with col2:
        st.write(local_text["eisenhower_title"])
        st.write(local_text["eisenhower_desc"])
        st.image(
            "/app/src/ui/img/eisenhower.png", caption="Eisenhower Matrix, Wikipedia", width=250
        )
        st.markdown(
            f"[{local_text['eisenhower_link']}](https://en.wikipedia.org/wiki/Time_management#Eisenhower_method)"
        )

    st.divider()
    st.write(local_text["summary"])
    st.write(local_text["irony"])

    if st.button(local_text["close"]):
        st.rerun()


@st.dialog(TEXTS["generic"]["settings_dialog"], width="small")
def show_settings_dialog():
    """Displays the settings dialog."""
    local_text = get_local_text()["settings"]

    language_options = {key for key, _ in TEXTS.items() if key != "generic"}

    left, right = st.columns([0.3, 0.7])
    with left:
        st.markdown(local_text["language"] + ":", help=local_text["language_desc"])
    with right:
        selected_language = st.selectbox(
            local_text["language"],
            options=list(language_options),
            index=list(language_options).index(st.session_state.settings["LANGUAGE"]),
            key="language_selection",
            label_visibility="collapsed",
        )

    left, right = st.columns([0.3, 0.7])
    with left:
        st.markdown(local_text["timezone"] + ":", help=local_text["timezone_desc"])
    with right:
        selected_timezone = st.selectbox(
            local_text["timezone"],
            options=pytz.all_timezones,
            index=pytz.all_timezones.index(st.session_state.settings["TIMEZONE"]),
            key="timezone_selection",
            label_visibility="collapsed",
        )

    left, right = st.columns([0.3, 0.7])
    with left:
        st.markdown(local_text["model"] + ":", help=local_text["model_desc"])
    with right:
        model_options = set(MODELS)
        model_options.add(st.session_state.settings["MODEL"])
        model_options = sorted(model_options)
        selected_model = st.selectbox(
            label="Model",
            options=list(model_options),
            index=list(model_options).index(st.session_state.settings["MODEL"]),
            key="model_selection",
            label_visibility="collapsed",
            accept_new_options=True,
        )

    left, right = st.columns([0.3, 0.7])
    with left:
        st.markdown(local_text["page_size"] + ":", help=local_text["page_size_desc"])
    with right:
        page_size_options = set(
            ["5", "10", "25", str(st.session_state.settings["PAGE_SIZE"])]
        )
        page_size_options = sorted(page_size_options, key=int)
        selected_page_size = st.selectbox(
            label="PageSize",
            options=list(page_size_options),
            index=list(page_size_options).index(
                str(st.session_state.settings["PAGE_SIZE"])
            ),
            key="page_size_selection",
            label_visibility="collapsed",
            accept_new_options=True,
        )

    left, center, right = st.columns([0.3, 0.2, 0.5])
    with left:
        st.markdown(local_text["wipe_db"] + ":", help=local_text["wipe_db_desc"])
    with center:
        if st.button(
            TEXTS["generic"]["trash"],
            key="wipe_db_button",
            use_container_width=True,
        ):
            with st.spinner(""):
                time.sleep(2)
                delete_db()
    with right:
        keep_favorites = st.checkbox(
            local_text["keep_favorites"],
            value=True,
            key="keep_favorites_checkbox",
        )
        st.session_state.keep_favorites = True if keep_favorites else False

    if st.button(local_text["save"]):
        st.session_state.settings["LANGUAGE"] = selected_language
        st.session_state.settings["TIMEZONE"] = selected_timezone
        st.session_state.settings["MODEL"] = selected_model
        st.session_state.settings["PAGE_SIZE"] = int(selected_page_size)
        save_settings()
        st.rerun()


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


def render_ui():
    """Main function to render the UI components and handle state."""
    handle_states()
    setup_page()
    setup_custom_styles()
    render_header_elements()

    fetch_latest_tasks()
    render_tasks(st.container())

    render_pagination()
    render_loading_spinner()
