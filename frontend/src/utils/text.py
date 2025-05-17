import streamlit as st
from config.constants import TEXTS


def get_local_text():
    return TEXTS[st.session_state.settings["LANGUAGE"]]
