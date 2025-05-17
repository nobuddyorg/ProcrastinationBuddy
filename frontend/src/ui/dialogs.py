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
        _render_help_section(
            title=local_text["pomodoro_title"],
            desc=local_text["pomodoro_desc"],
            image_path="/app/src/ui/img/pomodoro.png",
            caption="Pomodoro Technique, Wikipedia",
            link=local_text["pomodoro_link"],
            url="https://en.wikipedia.org/wiki/Pomodoro_Technique",
        )

    with col2:
        _render_help_section(
            title=local_text["eisenhower_title"],
            desc=local_text["eisenhower_desc"],
            image_path="/app/src/ui/img/eisenhower.png",
            caption="Eisenhower Matrix, Wikipedia",
            link=local_text["eisenhower_link"],
            url="https://en.wikipedia.org/wiki/Time_management#Eisenhower_method",
        )

    st.divider()
    st.write(local_text["summary"])
    st.write(local_text["irony"])

    if st.button(local_text["close"]):
        st.rerun()


def _render_help_section(title, desc, image_path, caption, link, url):
    st.write(title)
    st.write(desc)
    st.image(image_path, caption=caption, width=250)
    st.markdown(f"[{link}]({url})")


@st.dialog(TEXTS["generic"]["settings_dialog"], width="small")
def show_settings_dialog():
    """Displays the settings dialog."""
    local_text = get_local_text()["settings"]

    # Language
    language_options = sorted(k for k in TEXTS if k != "generic")
    selected_language = _render_select_setting(
        label=local_text["language"],
        help_text=local_text["language_desc"],
        options=language_options,
        current_value=st.session_state.settings["LANGUAGE"],
        key="language_selection",
    )

    # Timezone
    selected_timezone = _render_select_setting(
        label=local_text["timezone"],
        help_text=local_text["timezone_desc"],
        options=pytz.all_timezones,
        current_value=st.session_state.settings["TIMEZONE"],
        key="timezone_selection",
    )

    # Model
    model_options = sorted(set(MODELS).union({st.session_state.settings["MODEL"]}))
    selected_model = _render_select_setting(
        label=local_text["model"],
        help_text=local_text["model_desc"],
        options=model_options,
        current_value=st.session_state.settings["MODEL"],
        key="model_selection",
        accept_new=True,
    )

    # Page Size
    current_size = str(st.session_state.settings["PAGE_SIZE"])
    page_sizes = sorted(set(["5", "10", "25", current_size]), key=int)
    selected_page_size = _render_select_setting(
        label=local_text["page_size"],
        help_text=local_text["page_size_desc"],
        options=page_sizes,
        current_value=current_size,
        key="page_size_selection",
        accept_new=True,
    )

    # Delete + Keep Favorites
    _render_delete_controls(local_text)

    # Save Button
    if st.button(local_text["save"]):
        st.session_state.settings.update(
            {
                "LANGUAGE": selected_language,
                "TIMEZONE": selected_timezone,
                "MODEL": selected_model,
                "PAGE_SIZE": int(selected_page_size),
            }
        )
        save_settings()
        st.rerun()


def _render_select_setting(
    label, help_text, options, current_value, key, accept_new=False
):
    left, right = st.columns([0.3, 0.7])
    with left:
        st.markdown(label + ":", help=help_text)
    with right:
        return st.selectbox(
            label,
            options=list(options),
            index=list(options).index(current_value),
            key=key,
            label_visibility="collapsed",
            accept_new_options=accept_new,
        )


def _render_delete_controls(local_text):
    left, center, right = st.columns([0.3, 0.2, 0.5])
    with left:
        st.markdown(local_text["wipe_db"] + ":", help=local_text["wipe_db_desc"])
    with center:
        if st.button(
            TEXTS["generic"]["trash"], key="wipe_db_button", use_container_width=True
        ):
            with st.spinner(""):
                time.sleep(2)
                delete_tasks()
    with right:
        keep = st.checkbox(
            local_text["keep_favorites"], value=True, key="keep_favorites_checkbox"
        )
        st.session_state.keep_favorites = keep
