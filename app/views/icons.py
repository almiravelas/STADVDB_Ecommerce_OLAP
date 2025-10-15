import streamlit as st

ORANGE = "#ff4b4b"

def _inject_icon_css():
    st.markdown(
        f"""
        <style>
          .ui-icon {{
            display: inline-flex;
            align-items: center;
            gap: .5rem;
            font-weight: 700;
            line-height: 1.2;
            margin: .25rem 0 .5rem 0;
          }}
          .ui-icon svg {{
            width: 18px; height: 18px; fill: {ORANGE}; flex: 0 0 auto;
          }}
          /* Title (bigger) */
          .ui-title {{
            font-size: 1.6rem;   /* page title size */
            margin: .25rem 0 .75rem 0;
          }}
          /* Section headers (medium) */
          .ui-section {{
            font-size: 1.15rem;  /* section header size */
            margin: .25rem 0 .5rem 0;
          }}
        </style>
        """,
        unsafe_allow_html=True
    )

def _svg(kind: str) -> str:
    icons = {
        "truck": """<svg viewBox="0 0 24 24"><path d="M3 6h11v8H3zM14 9h4l3 3v2h-7zM7 18a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm10 0a2 2 0 1 0 .001-3.999A2 2 0 0 0 17 18z"/></svg>""",
        "calendar": """<svg viewBox="0 0 24 24"><path d="M7 2h2v2h6V2h2v2h1a2 2 0 0 1 2 2v4H3V6a2 2 0 0 1 2-2h1V2zM3 10h18v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-9z"/></svg>""",
        "user": """<svg viewBox="0 0 24 24"><path d="M12 12a5 5 0 1 0 0-10 5 5 0 0 0 0 10zm0 2c-5.33 0-8 2.67-8 6v2h16v-2c0-3.33-2.67-6-8-6z"/></svg>""",
        "filter": """<svg viewBox="0 0 24 24"><path d="M3 5h18v2l-7 7v5l-4-2v-3L3 7z"/></svg>""",
        "chart": """<svg viewBox="0 0 24 24"><path d="M3 20h18v2H3zM5 10h3v8H5zM11 6h3v12h-3zM17 13h3v5h-3z"/></svg>""",
        "table": """<svg viewBox="0 0 24 24"><path d="M3 5h18v14H3zM3 9h18M9 5v14M15 5v14"/></svg>""",
        "data": """<svg viewBox="0 0 24 24"><path d="M12 2c-4 0-7 1.79-7 4v12c0 2.21 3 4 7 4s7-1.79 7-4V6c0-2.21-3-4-7-4zm0 2c3.31 0 5 .9 5 2s-1.69 2-5 2-5-.9-5-2 1.69-2 5-2zm0 16c-3.31 0-5-.9-5-2v-2c1.11.68 3.12 1 5 1s3.89-.32 5-1v2c0 1.1-1.69 2-5 2zm0-6c-3.31 0-5-.9-5-2v-2c1.11.68 3.12 1 5 1s3.89-.32 5-1v2c0 1.1-1.69 2-5 2z"/></svg>""",
        "metrics": """<svg viewBox="0 0 24 24"><path d="M3 17h3V9H3v8zm5 0h3V5H8v12zm5 0h3v-6h-3v6zm5 0h3V3h-3v14z"/></svg>""",
    }
    return icons.get(kind, "")

def _icon(text: str, kind: str, is_title: bool = False):
    cls = "ui-icon ui-title" if is_title else "ui-icon ui-section"
    st.markdown(f'<div class="{cls}">{_svg(kind)}<span>{text}</span></div>', unsafe_allow_html=True)

def _inject_icon_css():
    st.markdown(
        f"""
        <style>
          .ui-icon {{
            display: inline-flex;
            align-items: center;
            gap: .5rem;
            font-weight: 700;
            line-height: 1.2;
            margin: .25rem 0 .5rem 0;
          }}
          .ui-icon svg {{
            width: 18px; height: 18px; fill: {ORANGE}; flex: 0 0 auto;
          }}

          /* Page title */
          .ui-title {{
            font-size: 1.6rem;
            margin: .2rem 0 .9rem 0;
          }}

          /* Section headers */
          .ui-section {{
            font-size: 1.15rem;
            margin: .2rem 0 .5rem 0;
          }}

          /* ---------- Fix ellipsis in st.metric values ---------- */
          div[data-testid="stMetricValue"] > div {{
            overflow: visible !important;
            text-overflow: clip !important;
            white-space: nowrap !important;
          }}
          div[data-testid="stMetricValue"] {{
            font-variant-numeric: tabular-nums;
          }}
        </style>
        """,
        unsafe_allow_html=True
    )

def _svg(kind: str) -> str:
    icons = {
        "dashboard": """<svg viewBox="0 0 24 24"><path d="M3 3h8v8H3zM13 3h8v5h-8zM13 10h8v11h-8zM3 13h8v8H3z"/></svg>""",
        "calendar": """<svg viewBox="0 0 24 24"><path d="M7 2h2v2h6V2h2v2h1a2 2 0 0 1 2 2v4H3V6a2 2 0 0 1 2-2h1V2zM3 10h18v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-9z"/></svg>""",
        "metrics": """<svg viewBox="0 0 24 24"><path d="M3 17h3V9H3v8zm5 0h3V5H8v12zm5 0h3v-6h-3v6zm5 0h3V3h-3v14z"/></svg>""",
        "chart": """<svg viewBox="0 0 24 24"><path d="M3 20h18v2H3zM5 10h3v8H5zM11 6h3v12h-3zM17 13h3v5h-3z"/></svg>""",
    }
    return icons.get(kind, "")

def _icon(text: str, kind: str, is_title: bool = False):
    cls = "ui-icon ui-title" if is_title else "ui-icon ui-section"
    st.markdown(f'<div class="{cls}">{_svg(kind)}<span>{text}</span></div>', unsafe_allow_html=True)
    
def _inject_extra_css():
    st.markdown(
        """
        <style>
          /* Prevent truncation/ellipsis in st.metric values */
          div[data-testid="stMetricValue"] > div {
            overflow: visible !important;
            text-overflow: clip !important;
            white-space: nowrap !important;
          }
          div[data-testid="stMetricValue"] { font-variant-numeric: tabular-nums; }
        </style>
        """,
        unsafe_allow_html=True
    )