import streamlit as st


def inject_custom_css():
    """
    Inject custom CSS enforcing §8.2 Design Tokens from Cahier des Charges & DESIGN.md:
    - Surface: #101416
    - Container/Cards: #1D2022
    - Sidebar: #0B0F11
    - Primary Teal: #78D8BA
    - Secondary Cyan/Light Blue: #81D0F8
    - Critical Red/Pink: #FFB4AB
    - Warning Amber: #D98E1E
    - Monospace font: JetBrains Mono
    - Headline font: IBM Plex Sans
    - Body font: Inter
    """
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {
        --surface: #101416;
        --surface-container: #1D2022;
        --surface-container-high: #272A2D;
        --surface-sidebar: #0B0F11;
        --primary: #78D8BA;
        --secondary: #81D0F8;
        --tertiary: #A7C8FF;
        --error: #FFB4AB;
        --warning: #D98E1E;
        --success: #2E9E5B;
        --outline: #3E4945;
        --text-on-surface: #E0E3E6;
        --text-muted: #BDC9C3;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: var(--surface) !important;
        color: var(--text-on-surface) !important;
    }

    .stApp {
        background-color: var(--surface) !important;
    }

    /* Sidebar background */
    [data-testid="stSidebar"] {
        background-color: var(--surface-sidebar) !important;
        border-right: 1px solid var(--outline);
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'IBM Plex Sans', sans-serif !important;
        color: var(--primary) !important;
        font-weight: 600 !important;
    }

    /* Cards */
    .sentinelle-card {
        background-color: var(--surface-container);
        border: 1px solid var(--outline);
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 16px;
        transition: all 0.2s ease-in-out;
    }
    .sentinelle-card:hover {
        border-color: var(--primary);
    }

    .sentinelle-card-critical {
        background-color: var(--surface-container);
        border: 1px solid var(--error);
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 0 12px rgba(255, 180, 171, 0.25);
    }

    .sentinelle-card-warning {
        background-color: var(--surface-container);
        border: 1px solid var(--warning);
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 0 10px rgba(217, 142, 30, 0.2);
    }

    .sentinelle-card-healthy {
        background-color: var(--surface-container);
        border: 1px solid var(--primary);
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 16px;
    }

    /* KPI Cards */
    .sentinelle-kpi-card {
        background-color: var(--surface-container);
        border: 1px solid var(--outline);
        border-radius: 8px;
        padding: 16px;
        text-align: left;
    }
    .sentinelle-kpi-title {
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .sentinelle-kpi-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 28px;
        font-weight: 700;
        color: var(--primary);
    }
    .sentinelle-kpi-sub {
        font-size: 12px;
        color: var(--text-muted);
        margin-top: 4px;
    }

    /* Monospace Text */
    .sentinelle-mono {
        font-family: 'JetBrains Mono', monospace !important;
        color: var(--primary);
    }
    .sentinelle-mono-critical {
        font-family: 'JetBrains Mono', monospace !important;
        color: var(--error);
    }
    .sentinelle-mono-secondary {
        font-family: 'JetBrains Mono', monospace !important;
        color: var(--secondary);
    }
    .sentinelle-mono-warning {
        font-family: 'JetBrains Mono', monospace !important;
        color: var(--warning);
    }

    /* Status Badges */
    .sentinelle-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        font-weight: 600;
    }
    .sentinelle-badge-critical {
        background-color: rgba(255, 180, 171, 0.15);
        color: var(--error);
        border: 1px solid var(--error);
    }
    .sentinelle-badge-warning {
        background-color: rgba(217, 142, 30, 0.15);
        color: var(--warning);
        border: 1px solid var(--warning);
    }
    .sentinelle-badge-healthy {
        background-color: rgba(120, 216, 186, 0.15);
        color: var(--primary);
        border: 1px solid var(--primary);
    }

    /* Code Diff Styling */
    .sentinelle-diff-container {
        font-family: 'JetBrains Mono', monospace;
        background-color: #0B0F11;
        border: 1px solid var(--outline);
        border-radius: 6px;
        padding: 12px;
        font-size: 13px;
        line-height: 1.6;
        white-space: pre-wrap;
    }
    .sentinelle-diff-remove {
        background-color: rgba(255, 180, 171, 0.15);
        color: #FFB4AB;
        display: block;
        padding: 2px 8px;
        border-left: 3px solid #FFB4AB;
    }
    .sentinelle-diff-add {
        background-color: rgba(120, 216, 186, 0.15);
        color: #78D8BA;
        display: block;
        padding: 2px 8px;
        border-left: 3px solid #78D8BA;
    }

    /* Chat Copilot Styling */
    .sentinelle-chat-bubble-user {
        background-color: #1C4476;
        border: 1px solid var(--secondary);
        border-radius: 12px 12px 2px 12px;
        padding: 12px 16px;
        margin: 8px 0;
        float: right;
        clear: both;
        max-width: 80%;
    }
    .sentinelle-chat-bubble-ai {
        background-color: var(--surface-container);
        border: 1px solid var(--outline);
        border-radius: 12px 12px 12px 2px;
        padding: 14px 18px;
        margin: 8px 0;
        float: left;
        clear: both;
        max-width: 85%;
    }
    .sentinelle-readonly-badge {
        background-color: rgba(129, 208, 248, 0.15);
        color: var(--secondary);
        border: 1px solid var(--secondary);
        padding: 4px 12px;
        border-radius: 9999px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        font-weight: 600;
    }

    /* Buttons */
    .stButton>button {
        background-color: var(--primary) !important;
        color: #101416 !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 8px 16px !important;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: var(--secondary) !important;
        color: #101416 !important;
        box-shadow: 0 0 10px rgba(129, 208, 248, 0.4);
    }

    /* Inputs */
    .stTextInput input, .stSelectbox select {
        background-color: #0B0F11 !important;
        color: var(--text-on-surface) !important;
        border: 1px solid var(--outline) !important;
        border-radius: 6px !important;
    }
    .stTextInput input:focus {
        border-color: var(--secondary) !important;
        box-shadow: 0 0 6px rgba(129, 208, 248, 0.3) !important;
    }

    /* Tables */
    [data-testid="stDataFrame"] {
        background-color: var(--surface-container) !important;
        border: 1px solid var(--outline) !important;
        border-radius: 8px !important;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

