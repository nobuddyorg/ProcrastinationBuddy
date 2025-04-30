import requests
import streamlit as st
import time
from constants import BACKEND_URL, PAGE_ICON, LAYOUT, TEXTS, LANGUAGE
from datetime import datetime
from streamlit_theme import st_theme
from email.utils import parsedate_to_datetime


def set_page_config():
    st.set_page_config(
        page_title=TEXTS[LANGUAGE]['main']['title'],
        page_icon=PAGE_ICON,
        layout=LAYOUT,
    )
    
def set_title():
    st.title(TEXTS[LANGUAGE]['main']['title'])
    
def set_subtitle():
    st.markdown(f"<h5 style='margin-top: -20px; font-size: 16px; font-style: italic;'>{TEXTS[LANGUAGE]['main']['subtitle']}</h5>", unsafe_allow_html=True)
    
def set_styles():
    st.markdown("""
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
        </style>
    """, unsafe_allow_html=True)

def hide_streamlit_style():
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)


@st.dialog(TEXTS[LANGUAGE]['help']['title'], width="large")
def show_dialog():
    text = TEXTS[LANGUAGE]["help"]
    if "images_ready" not in st.session_state:
        with st.spinner(text["loading_text"]):
            time.sleep(1)
            st.session_state.images_ready = True
            
    st.write(text["intro"])
    st.write(text["middle"])

    col1, col2 = st.columns(2)
    with col1:
        st.write(text["pomodoro_title"])
        st.write(text["pomodoro_desc"])
        st.image("img/pomodoro.png", caption="Pomodoro Technique, Wikipedia", width=250)
        st.write(f"[{text['pomodoro_link']}](https://en.wikipedia.org/wiki/Pomodoro_Technique)")

    with col2:
        st.write(text["eisenhower_title"])
        st.write(text["eisenhower_desc"])
        st.image("img/eisenhower.png", caption="Eisenhower Matrix, Wikipedia", width=250)
        st.write(f"[{text['eisenhower_link']}](https://en.wikipedia.org/wiki/Time_management#Eisenhower_method)")

    st.divider()
    st.write(text["summary"])
    st.write(text["irony"])

    if st.button(text["close"]):
        st.rerun()


def generate_task():
    try:
        response = requests.get(f"{BACKEND_URL}/procrastinate")
        response.raise_for_status()
        task_text = response.json()['task'].strip('"')

        task_entry = {
            'text': task_text,
            'time': datetime.now().strftime("%H:%M:%S")
        }

        if 'task_list' not in st.session_state:
            st.session_state.task_list = []

        st.session_state.task_list.insert(0, task_entry)
        st.session_state.task_list = st.session_state.task_list[:10]

        return task_text
    except requests.exceptions.RequestException as e:
        st.error(f"Error generating task from {BACKEND_URL}: {e}")
        return "Failed to get a task."

def handle_button_state():
    """
    Handles the state of the generate button, managing whether it should be disabled or not.
    """
    if 'generate_button' in st.session_state and st.session_state.generate_button:
        st.session_state.running = True
    else:
        st.session_state.running = False

def display_task(tasks_container):
    """
    Displays the last 10 generated tasks with timestamps, with a different background for tasks in both light and dark modes.
    """
    theme_info = st_theme()
    if theme_info:
        st.session_state['theme_base'] = theme_info.get('base')

    theme = st.session_state.get('theme_base', 'light')
    task_background_color = "#333333" if theme == 'dark' else "#f0f0f0"
    text_color = st.get_option('theme.textColor')
    
    with tasks_container:
        if 'task_list' in st.session_state and st.session_state.task_list:
            recent_tasks = st.session_state.task_list[:10]
            
            for idx, task in enumerate(recent_tasks):
                offset = "25px"
                margin_left = offset if idx % 2 == 1 else "0px"
                st.markdown(
                    f"<div style='background-color: {task_background_color}; width: calc(80% - {offset}); padding: 10px; border-radius: 5px; "
                    f"font-size: 14px; margin-bottom: 5px; margin-left: {margin_left}; color: {text_color};'>"
                    f"<strong>{task['time']}:</strong> {task['text']}</div>",
                    unsafe_allow_html=True
                )
            
def fetch_latest_tasks():
    try:
        response = requests.get(f"{BACKEND_URL}/tasks", params={"skip": 0, "limit": 10})
        response.raise_for_status()
        task_data = response.json()

        st.session_state.task_list = [
            {
                'text': task['task_text'],
                'time': parsedate_to_datetime(task['created_at']).astimezone().strftime("%H:%M:%S")
            } for task in task_data
        ]
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching tasks: {e}")
