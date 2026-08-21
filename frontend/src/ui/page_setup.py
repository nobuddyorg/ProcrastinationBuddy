import base64
from pathlib import Path

import streamlit as st

from config.constants import LAYOUT, TEXTS
from utils.text import get_generic_text

LOGO_PATH = Path(__file__).parent / "img" / "procrastination-logo.webp"
WORDMARK_FONT_PATH = Path(__file__).parent / "vendor" / "fonts" / "archivo-700.woff2"


def _logo_data_uri() -> str:
    encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return f"data:image/webp;base64,{encoded}"


def _wordmark_font_data_uri() -> str:
    encoded = base64.b64encode(WORDMARK_FONT_PATH.read_bytes()).decode("ascii")
    return f"data:font/woff2;base64,{encoded}"


def setup_page():
    """Sets up the Streamlit page configuration."""
    st.set_page_config(
        page_title=get_generic_text()["title"],
        page_icon=str(LOGO_PATH),
        layout=LAYOUT,
    )
    subtitle = TEXTS[st.session_state.settings["LANGUAGE"]]["main"]["subtitle"]
    st.markdown(
        f"""
        <div class="pb-header">
            <h1 class="pb-wordmark">
                <img class="pb-logo" src="{_logo_data_uri()}" alt="" /><span class="pb-ruled">Procrastination</span><span class="pb-accent">Buddy</span>
            </h1>
            <p class="pb-subtitle">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def setup_custom_styles():
    """Applies custom CSS styles to the Streamlit app."""
    font_face_css = f"""
        @font-face {{
            font-family: 'Archivo';
            font-style: normal;
            font-weight: 700;
            font-display: swap;
            src: url('{_wordmark_font_data_uri()}') format('woff2');
        }}
    """
    st.markdown(
        f"""
        <style>
        {font_face_css}
        pre {{
            margin-bottom: -0.3rem !important;
        }}
        .stApp .row-widget.stColumns {{
            column-gap: 0rem !important;
        }}
        .stApp .stColumn {{
            padding: 0 !important;
            margin: 0 !important;
        }}
        .stSpinner > div {{
            margin-top: 0.45rem !important;
        }}
        [data-testid="stBaseButton-pills"],
        [data-testid="stBaseButton-pillsActive"] {{
            margin-top: 0.3rem !important;
            margin-bottom: -0.3rem !important;
        }}
        [data-testid="stProgressBarTrack"] > div {{
            background-color: #FF4B4B !important;
        }}
        #MainMenu, footer, header {{
            visibility: hidden !important;
        }}

        :root {{
            --pb-wordmark-accent-light: #AD5725;
            --pb-wordmark-accent-dark: #E0954F;
        }}
        .pb-header {{
            position: sticky;
            top: 0;
            z-index: 999;
            padding: calc(env(safe-area-inset-top, 0px) + 0.75rem) 0.5rem 0.9rem;
            margin-bottom: 0.5rem;
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            background: rgba(255, 255, 255, 0.9);
            border-bottom: 1px solid rgba(49, 51, 63, 0.15);
        }}
        .pb-wordmark {{
            font-family: 'Archivo', -apple-system, BlinkMacSystemFont,
                'Segoe UI', Roboto, sans-serif;
            font-weight: 700;
            font-size: 2rem;
            line-height: 1.2;
            letter-spacing: -0.02em;
            display: flex;
            align-items: center;
            margin: 0;
            padding-bottom: 2px;
        }}
        .pb-wordmark .pb-logo {{
            height: 2.5rem;
            width: 2.5rem;
            margin-right: 0.5rem;
            flex-shrink: 0;
            object-fit: contain;
        }}
        .pb-wordmark .pb-ruled {{
            border-bottom: 3px solid currentColor;
            padding-bottom: 2px;
        }}
        .pb-wordmark .pb-accent {{
            color: var(--pb-wordmark-accent-light);
        }}
        .pb-subtitle {{
            font-style: italic;
            font-size: 16px;
            margin: 0.15rem 0 0 0;
        }}
        @media (prefers-color-scheme: dark) {{
            .pb-header {{
                background: rgba(14, 17, 23, 0.9);
                border-bottom-color: rgba(250, 250, 250, 0.15);
            }}
            .pb-wordmark .pb-accent {{
                color: var(--pb-wordmark-accent-dark);
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
