import streamlit as st
from constants import TITLE, DESCRIPTION, GENERATE_BUTTON_TEXT, SPINNER_TEXT
from utils import set_page_config, hide_streamlit_style, generate_task, handle_button_state, display_task, set_styles

def main():
    set_page_config()
    st.title(TITLE)
    st.markdown(f"<h5 style='margin-top: -20px; font-size: 16px; font-style: italic;'>{DESCRIPTION}</h5>", unsafe_allow_html=True)
    
    hide_streamlit_style()
    set_styles()

    handle_button_state()

    col1, col2 = st.columns([0.15, 0.85], border=False)
    with col2:
        placeholder = st.empty()
    with col1:
        if st.button(GENERATE_BUTTON_TEXT, disabled=st.session_state.running, key='generate_button'):
            with placeholder, st.spinner(SPINNER_TEXT):
                task = generate_task()
                st.session_state.task = task
            st.rerun()

    display_task()

if __name__ == "__main__":
    main()
