import streamlit as st
from constants import TITLE, GENERATE_BUTTON_TEXT, SPINNER_TEXT
from utils import set_page_config, hide_streamlit_style, generate_task, handle_button_state, display_task, set_styles, show_dialog, set_subtitle, fetch_latest_tasks

def main():
    set_page_config()
    st.title(TITLE)
    set_subtitle()

    hide_streamlit_style()
    set_styles()

    handle_button_state()
    
    if 'task_list' not in st.session_state:
        fetch_latest_tasks()

    col1, col2, col3 = st.columns([0.15, 0.1, 0.75], border=False)
    with col3:
        placeholder = st.empty()
    with col1:
        if st.button(GENERATE_BUTTON_TEXT, disabled=st.session_state.running, key='generate_button'):
            with placeholder, st.spinner(SPINNER_TEXT):
                task = generate_task()
                st.session_state.task = task
            st.rerun()
    with col2:
        if st.button("ℹ️"):
            show_dialog()

    display_task()

if __name__ == "__main__":
    main()
