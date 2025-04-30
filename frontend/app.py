import streamlit as st
from constants import TEXTS, LANGUAGE
from utils import set_page_config, hide_streamlit_style, generate_task, handle_button_state, display_task, set_styles, show_dialog, set_subtitle, fetch_latest_tasks, set_title

def main():
    set_page_config()
    set_title()
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
        if st.button(TEXTS[LANGUAGE]['main']['generate_button'], disabled=st.session_state.running, key='generate_button'):
            with placeholder, st.spinner(TEXTS[LANGUAGE]['main']['spinner_text']):
                task = generate_task()
                st.session_state.task = task
            st.rerun()
    with col2:
        if st.button(TEXTS[LANGUAGE]['main']['info_button']):
            show_dialog()
            
    display_task(st.container())

if __name__ == "__main__":
    main()
