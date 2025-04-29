import requests
import streamlit as st
from constants import BACKEND_URL, TITLE, PAGE_ICON, LAYOUT, DESCRIPTION
from datetime import datetime
from streamlit_theme import st_theme

def set_page_config():
    st.set_page_config(
        page_title=TITLE,
        page_icon=PAGE_ICON,
        layout=LAYOUT,
    )
    
def set_subtitle():
    st.markdown(f"<h5 style='margin-top: -20px; font-size: 16px; font-style: italic;'>{DESCRIPTION}</h5>", unsafe_allow_html=True)
    
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

@st.dialog("Why other tools don't help you!", width="large")
def show_dialog():
    st.write("""
        **Let's face it**, you’ll end up in the *'Urgent and Important'* quadrant of the Eisenhower Matrix anyway. 
        Why waste time planning? Pomodoro? Sure, take a 25-minute break. Procrastination isn't a sprint, it's art.
    """)

    st.write("""
        But hey, don’t stress, just enjoy your perfectly unbalanced balance of procrastination and productivity. 
        And if you're still trying to stick to these methods against all reason, feel free to read more about them.
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.write("""
            **Pomodoro Technique**: It’s all about 25-minute bursts of productivity… or of pretending to focus until your next scheduled distraction. 
            Maybe you get something done - or maybe you procrastinate harder, just to avoid the timer. Either way, say goodbye to focus and farewell to flow.
        """)
            
        st.image("img/pomodoro.png", caption="Pomodoro Technique, Wikipedia", width=250)
        st.write("[Learn more about Pomodoro Technique](https://en.wikipedia.org/wiki/Pomodoro_Technique)")

    with col2:
        st.write("""
            **Eisenhower Matrix**: It’s a fancy way of making all your tasks urgent and important at the same time.
            Congratulations, you're officially stressed - staring at one remaining quadrant with no method left to help with priorities anymore. Probably best to just do something else entirely!
        """)
        st.image("img/eisenhower.png", caption="Eisenhower Matrix, Wikipedia", width=250)
        st.write("[Learn more about Eisenhower Matrix](https://en.wikipedia.org/wiki/Time_management#Eisenhower_method)")

    st.divider()
    
    st.write("""
        In the end, these methods might help. But when you're truly embracing procrastination, remember: *all tasks will end up in 'Urgent and Important'*. 
        Deadlines will shove you into *no-break mode*, and somehow, you’ll still manage to *avoid* the so called important tasks.
    """)
    
    st.write("""
        **If you think this is sarcastic, just remember: it's still not as ironic as using a tomato or a 60-year-old matrix to boost your productivity in the 21st century as if the world hasn’t changed since.**
    """)

    if st.button("Close"):
        st.rerun()

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
        st.session_state['theme_base'] = theme_info.get('base')

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
