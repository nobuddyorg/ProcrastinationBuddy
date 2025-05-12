import streamlit as st
from streamlit_javascript import st_javascript
from constants import TEXTS, LANGUAGE
from utils import (
    set_page_config,
    hide_streamlit_style,
    generate_task,
    handle_button_state,
    display_task,
    set_styles,
    show_dialog,
    set_subtitle,
    fetch_latest_tasks,
    set_title,
)


def main():
    set_page_config()
    set_title()
    set_subtitle()

    hide_streamlit_style()
    set_styles()

    handle_button_state()

    if "task_list" not in st.session_state:
        fetch_latest_tasks()

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
            label="Filter Likes",
            key="feedback_filter",
            disabled=st.session_state.running,
        )
    with col5:
        if st.session_state.running:
            st.session_state.running = False
            with st.spinner(TEXTS[LANGUAGE]["main"]["spinner_text"]):
                generate_task()
                st.rerun()
        else:
            st.empty()

    if not st.session_state.get("timezone"):
        timezone = st_javascript("""await (async () => {
            const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            console.log(userTimezone)
            return userTimezone
    })().then(returnValue => returnValue)""")
        if timezone:
            st.session_state["timezone"] = timezone

    if st.session_state.get("timezone"):
        display_task(st.container())


if __name__ == "__main__":
    main()
