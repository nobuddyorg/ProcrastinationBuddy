import streamlit as st
from config.constants import TEXTS, PAGE_ICON, LAYOUT
from utils.text import get_generic_text


def setup_page():
    """Sets up the Streamlit page configuration."""
    st.set_page_config(
        page_title=get_generic_text()["title"],
        page_icon=PAGE_ICON,
        layout=LAYOUT,
    )
    st.title(get_generic_text()["title"])
    st.markdown(
        f"<h5 style='margin-top: -20px; font-size: 16px; font-style: italic;'>{TEXTS[st.session_state.settings['LANGUAGE']]['main']['subtitle']}</h5>",
        unsafe_allow_html=True,
    )


def setup_custom_styles():
    """Applies custom CSS styles to the Streamlit app."""
    st.markdown(
        """
        <style>
        pre {
            margin-bottom: -0.3rem !important;
        }
        .stApp .row-widget.stColumns {
            column-gap: 0rem !important;
        }
        .stApp .stColumn {
            padding: 0 !important;
            margin: 0 !important;
        }
        .stSpinner > div {
            margin-top: 0.45rem !important;
        }
        [data-testid="stBaseButton-pills"],
        [data-testid="stBaseButton-pillsActive"] {
            margin-top: 0.3rem !important;
            margin-bottom: -0.3rem !important;
        }
        #MainMenu, footer, header {
            visibility: hidden !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
