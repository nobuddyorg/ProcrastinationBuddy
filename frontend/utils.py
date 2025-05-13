import requests
import streamlit as st
import pytz
from constants import BACKEND_URL, PAGE_ICON, LAYOUT, TEXTS, LANGUAGE
from datetime import datetime
from email.utils import parsedate_to_datetime
from streamlit_theme import st_theme


def set_page_config():
    st.set_page_config(
        page_title=TEXTS[LANGUAGE]["main"]["title"],
        page_icon=PAGE_ICON,
        layout=LAYOUT,
    )


def set_title():
    st.title(TEXTS[LANGUAGE]["main"]["title"])


def set_subtitle():
    st.markdown(
        f"<h5 style='margin-top: -20px; font-size: 16px; font-style: italic;'>{TEXTS[LANGUAGE]['main']['subtitle']}</h5>",
        unsafe_allow_html=True,
    )


def set_styles():
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
        
        [data-testid="stBaseButton-pills"] {
            margin-top: 5px;
            margin-bottom: -5px;
        }
        
        [data-testid="stBaseButton-pillsActive"] {
            margin-top: 5px;
            margin-bottom: -5px;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )


def hide_streamlit_style():
    st.markdown(
        """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """,
        unsafe_allow_html=True,
    )


@st.dialog(TEXTS[LANGUAGE]["help"]["title"], width="large")
def show_dialog():
    text = TEXTS[LANGUAGE]["help"]

    st.write(text["intro"])
    st.write(text["middle"])

    col1, col2 = st.columns(2)
    with col1:
        st.write(text["pomodoro_title"])
        st.write(text["pomodoro_desc"])
        st.image("img/pomodoro.png", caption="Pomodoro Technique, Wikipedia", width=250)
        st.write(
            f"[{text['pomodoro_link']}](https://en.wikipedia.org/wiki/Pomodoro_Technique)"
        )

    with col2:
        st.write(text["eisenhower_title"])
        st.write(text["eisenhower_desc"])
        st.image(
            "img/eisenhower.png", caption="Eisenhower Matrix, Wikipedia", width=250
        )
        st.write(
            f"[{text['eisenhower_link']}](https://en.wikipedia.org/wiki/Time_management#Eisenhower_method)"
        )

    st.divider()
    st.write(text["summary"])
    st.write(text["irony"])

    if st.button(text["close"]):
        st.rerun()


def generate_task():
    try:
        response = requests.get(f"{BACKEND_URL}/procrastinate")
        response.raise_for_status()
        task_text = response.json()["task"].strip('"')

        task_entry = {"text": task_text, "time": datetime.now().astimezone()}

        if "task_list" not in st.session_state:
            st.session_state.task_list = []

        st.session_state.task_list.insert(0, task_entry)
        st.session_state.task_list = st.session_state.task_list[:10]

        return task_text
    except requests.exceptions.RequestException as e:
        st.error(f"Error generating task from {BACKEND_URL}: {e}")
        return "Failed to get a task."


def handle_button_state():
    """
    Ensures 'running' is initialized.
    """
    if "running" not in st.session_state:
        st.session_state.running = False


def format_time(dt, timezone):
    tz = pytz.timezone(timezone)
    dt = dt.astimezone(tz)
    now = datetime.now(tz)

    if dt.date() == now.date():
        return dt.strftime("%H:%M:%S")
    else:
        return dt.strftime("%Y-%m-%d %H:%M:%S")


def get_task_content(task_background_color, text_color, timezone, task):
    st.markdown(
        f"<div style='background-color: {task_background_color}; width: 100%; padding: 10px; border-radius: 5px; "
        f"font-size: 14px; margin-bottom: 5px; color: {text_color};'>"
        f"<strong>{format_time(task['time'], timezone)}:</strong> {task['text']}</div>",
        unsafe_allow_html=True,
    )


def get_feedback_content(idx, task):
    with st.container():
        options = [TEXTS[LANGUAGE]["main"]["like_button"]]
        st.pills(
            label="feedback selection",
            options=options,
            selection_mode="single",
            key=f"feedback_{idx}",
            label_visibility="collapsed",
            default=options[0] if task.get("favorite", False) else None,
        )


def display_task(tasks_container):
    """
    Displays the last 10 generated tasks with timestamps, with a different background for tasks in both light and dark modes.
    """
    theme_info = st_theme()
    if theme_info:
        theme = theme_info.get("base")
        st.session_state["theme_base"] = theme
    theme = st.session_state.get("theme_base", "light")
    task_background_color = "#333333" if theme == "dark" else "#f0f0f0"
    text_color = st.get_option("theme.textColor")
    timezone = st.session_state.get("timezone")

    with tasks_container:
        if "task_list" in st.session_state and st.session_state.task_list:
            recent_tasks = st.session_state.task_list[:10]

            for idx, task in enumerate(recent_tasks):
                if idx % 2:
                    col1_size = 0.02
                    col2_size = 0.88
                    col3_size = 0.1
                else:
                    col1_size = 0.88
                    col2_size = 0.1
                    col3_size = 0.02
                col1, col2, col3 = st.columns(
                    [col1_size, col2_size, col3_size], border=False
                )

                with col1:
                    if idx % 2:
                        st.empty()
                    else:
                        get_task_content(
                            task_background_color, text_color, timezone, task
                        )
                with col2:
                    if idx % 2:
                        get_task_content(
                            task_background_color, text_color, timezone, task
                        )
                    else:
                        get_feedback_content(idx, task)

                with col3:
                    if idx % 2:
                        get_feedback_content(idx, task)
                    else:
                        st.empty()


def fetch_latest_tasks():
    try:
        response = requests.get(f"{BACKEND_URL}/tasks", params={"skip": 0, "limit": 10})
        response.raise_for_status()
        task_data = response.json()

        st.session_state.task_list = sorted(
            [
                {
                    "text": task["task_text"],
                    "time": parsedate_to_datetime(task["created_at"]),
                    "favorite": task["favorite"],
                }
                for task in task_data
            ],
            key=lambda task: task["time"],
            reverse=True,
        )

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching tasks: {e}")
