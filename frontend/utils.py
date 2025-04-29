import requests
import streamlit as st
from constants import BACKEND_URL, TITLE, PAGE_ICON, LAYOUT
from datetime import datetime
from streamlit_theme import st_theme

def set_page_config():
    st.set_page_config(
        page_title=TITLE,
        page_icon=PAGE_ICON,
        layout=LAYOUT,
    )
    
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

def generate_task():
    try:
        response = requests.get(BACKEND_URL)
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

def display_task():
    """
    Displays the last 10 generated tasks with timestamps, with a different background for tasks in both light and dark modes.
    """
    theme_info = st_theme()
    if theme_info:
        base = theme_info.get('base')
        print(base)
        st.session_state['theme_base'] = base
    else:
        print("No theme info available yet.")

    theme = st.session_state.get('theme_base', 'light')
    task_background_color = "#333333" if theme == 'dark' else "#f0f0f0"
    text_color = st.get_option('theme.textColor')

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
