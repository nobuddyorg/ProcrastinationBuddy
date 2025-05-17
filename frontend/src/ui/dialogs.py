import time
import streamlit as st
import pytz
from config.constants import TEXTS, MODELS
from utils.text import get_local_text
from utils.tasks_api import delete_tasks
from utils.settings_api import save_settings


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
        st.image(
            "/app/src/ui/img/pomodoro.png",
            caption="Pomodoro Technique, Wikipedia",
            width=250,
        )
        st.markdown(
            f"[{local_text['pomodoro_link']}](https://en.wikipedia.org/wiki/Pomodoro_Technique)"
        )

    with col2:
        st.write(local_text["eisenhower_title"])
        st.write(local_text["eisenhower_desc"])
        st.image(
            "/app/src/ui/img/eisenhower.png",
            caption="Eisenhower Matrix, Wikipedia",
            width=250,
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
                delete_tasks()
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
