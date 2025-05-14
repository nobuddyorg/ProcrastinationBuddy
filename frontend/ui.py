import streamlit as st
from streamlit_theme import st_theme
from constants import TEXTS, LANGUAGE, PAGE_ICON, LAYOUT
from utils import (
    generate_task,
    handle_button_state,
    setup_timezone,
    format_time,
    fetch_latest_tasks,
    set_as_favorite,
)


def setup_page():
    """Sets up the Streamlit page configuration."""
    st.set_page_config(
        page_title=TEXTS[LANGUAGE]["main"]["title"],
        page_icon=PAGE_ICON,
        layout=LAYOUT,
    )
    st.title(TEXTS[LANGUAGE]["main"]["title"])
    st.markdown(
        f"<h5 style='margin-top: -20px; font-size: 16px; font-style: italic;'>{TEXTS[LANGUAGE]['main']['subtitle']}</h5>",
        unsafe_allow_html=True,
    )


def setup_custom_styles():
    """Applies custom CSS styles to the Streamlit app."""
    st.markdown(
        """
        <style>
        .stApp .row-widget.stColumns {
            column-gap: 0rem !important;
        }
        .stApp .stColumn {
            padding: 0 !important;
            margin: 0 !important;
        }
        .stSpinner > div {
            margin-top: 7px;
        }
        [data-testid="stBaseButton-pills"],
        [data-testid="stBaseButton-pillsActive"] {
            margin-top: 5px;
            margin-bottom: -5px;
        }
        #MainMenu, footer, header {
            visibility: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header_elements():
    """Renders the header elements including buttons and loading spinner."""
    col1, col2, col3, col4, col5 = st.columns(
        [0.15, 0.1, 0.1, 0.19, 0.46], border=False
    )

    with col1:
        if st.button(
            TEXTS[LANGUAGE]["main"]["generate_button"],
            disabled=st.session_state.running,
            key="generate_button",
        ):
            st.session_state.running = True
            st.rerun()

    with col2:
        if st.button(
            TEXTS[LANGUAGE]["main"]["info_button"], disabled=st.session_state.running
        ):
            show_dialog()

    with col3:
        st.button(
            TEXTS[LANGUAGE]["main"]["config_button"], disabled=st.session_state.running
        )

    with col4:
        st.toggle(
            "Filter Likes", key="feedback_filter", disabled=st.session_state.running
        )

    with col5:
        st.session_state.loading_spinner = st.container()


def render_feedback(idx, task):
    """Renders feedback pill UI for a task."""
    options = [TEXTS[LANGUAGE]["main"]["like_button"]]
    selection = st.pills(
        label="feedback selection",
        options=options,
        selection_mode="single",
        key=f"feedback_{idx}",
        label_visibility="collapsed",
        default=options[0] if task.get("favorite", False) else None,
        disabled=st.session_state.running,
    )

    if selection:
        set_as_favorite(task["id"])
    else:
        set_as_favorite(task["id"], like=0)


def render_task(task, theme, timezone):
    """Renders a single task box with styling."""
    background_color = "#333333" if theme == "dark" else "#f0f0f0"
    text_color = st.get_option("theme.textColor")

    st.markdown(
        f"""
        <div style='background-color: {background_color}; padding: 10px; border-radius: 5px;
        font-size: 14px; color: {text_color}; margin-bottom: 5px;'>
            <strong>{format_time(task["time"], timezone)}:</strong> {task["text"]}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_tasks(container):
    """Displays up to 10 tasks with alternating layout and theme-based styling."""
    theme_info = st_theme()
    theme = theme_info.get("base") if theme_info else "light"
    st.session_state["theme_base"] = theme
    timezone = st.session_state.get("timezone", "UTC")

    with container:
        task_list = st.session_state.get("task_list", [])
        if not task_list:
            st.info("No tasks to display.")
            return

        for idx, task in enumerate(task_list[:10]):
            if idx % 2 == 0:
                left, middle, right = st.columns([0.88, 0.1, 0.02])
            else:
                left, middle, right = st.columns([0.02, 0.88, 0.1])

            with left:
                if idx % 2 == 0:
                    render_task(task, theme, timezone)
                else:
                    st.empty()

            with middle:
                if idx % 2 == 0:
                    render_feedback(idx, task)
                else:
                    render_task(task, theme, timezone)

            with right:
                if idx % 2 == 0:
                    st.empty()
                else:
                    render_feedback(idx, task)


def render_loading_spinner():
    """Displays a loading spinner while generating tasks."""
    with st.session_state.get("loading_spinner", st.container()):
        if st.session_state.running:
            with st.spinner(TEXTS[LANGUAGE]["main"]["spinner_text"]):
                generate_task()
                st.session_state.running = False
                st.rerun()
        else:
            st.empty()


@st.dialog(TEXTS[LANGUAGE]["help"]["title"], width="large")
def show_dialog():
    """Displays the sarcastic help/about dialog."""
    text = TEXTS[LANGUAGE]["help"]

    st.write(text["intro"])
    st.write(text["middle"])

    col1, col2 = st.columns(2)

    with col1:
        st.write(text["pomodoro_title"])
        st.write(text["pomodoro_desc"])
        st.image("img/pomodoro.png", caption="Pomodoro Technique, Wikipedia", width=250)
        st.markdown(
            f"[{text['pomodoro_link']}](https://en.wikipedia.org/wiki/Pomodoro_Technique)"
        )

    with col2:
        st.write(text["eisenhower_title"])
        st.write(text["eisenhower_desc"])
        st.image(
            "img/eisenhower.png", caption="Eisenhower Matrix, Wikipedia", width=250
        )
        st.markdown(
            f"[{text['eisenhower_link']}](https://en.wikipedia.org/wiki/Time_management#Eisenhower_method)"
        )

    st.divider()
    st.write(text["summary"])
    st.write(text["irony"])

    if st.button(text["close"]):
        st.rerun()


def render_ui():
    """Main function to render the UI components and handle state."""
    setup_page()
    setup_custom_styles()
    handle_button_state()
    render_header_elements()

    setup_timezone()
    if st.session_state.get("timezone"):
        if "task_list" not in st.session_state:
            fetch_latest_tasks()
        render_tasks(st.container())

    render_loading_spinner()
