"""
Estilos CSS para la app Semana SST - Clinica San Rafael Alta Complejidad SAS
Paleta: Azul clinica (#1565C0) + gris claro + acento verde
"""

THEME = {
    "primary": "#1565C0",       # azul institucional
    "primary_dark": "#0D47A1",
    "primary_light": "#5E92F3",
    "accent": "#2E7D32",        # verde clinico (acento)
    "accent_light": "#66BB6A",
    "warning": "#ED6C02",
    "danger": "#C62828",
    "success": "#2E7D32",
    "bg": "#F5F7FA",
    "bg_card": "#FFFFFF",
    "text": "#1A2332",
    "text_muted": "#5F6B7A",
    "border": "#E1E5EB",
    "shadow": "rgba(21, 101, 192, 0.08)",
}


CSS = f"""
<style>
/* ===== Reset y base ===== */
.stApp {{
    background: linear-gradient(135deg, #F5F7FA 0%, #E8EEF6 100%);
    color: {THEME['text']};
    font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
}}

/* ===== Header institucional ===== */
.app-header {{
    background: linear-gradient(135deg, {THEME['primary']} 0%, {THEME['primary_dark']} 100%);
    padding: 1.5rem 2rem;
    border-radius: 0 0 24px 24px;
    box-shadow: 0 6px 20px {THEME['shadow']};
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1.25rem;
    color: white;
}}
.app-header img {{
    height: 64px;
    width: auto;
    background: white;
    padding: 8px;
    border-radius: 12px;
}}
.app-header .titles h1 {{
    margin: 0;
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: -0.3px;
}}
.app-header .titles p {{
    margin: 4px 0 0 0;
    font-size: 0.95rem;
    opacity: 0.92;
    font-weight: 400;
}}

/* ===== Tarjetas ===== */
.card {{
    background: {THEME['bg_card']};
    border-radius: 18px;
    padding: 1.75rem;
    box-shadow: 0 4px 16px {THEME['shadow']};
    border: 1px solid {THEME['border']};
    margin-bottom: 1.25rem;
}}
.card-title {{
    font-size: 1.15rem;
    font-weight: 700;
    color: {THEME['primary_dark']};
    margin: 0 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid {THEME['primary_light']};
    display: flex;
    align-items: center;
    gap: 0.5rem;
}}
.card-subtitle {{
    font-size: 0.85rem;
    color: {THEME['text_muted']};
    margin-bottom: 1rem;
}}

/* ===== Botones personalizados ===== */
.stButton > button {{
    background: linear-gradient(135deg, {THEME['primary']} 0%, {THEME['primary_dark']} 100%);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.55rem 1.25rem;
    font-weight: 600;
    transition: all 0.2s ease;
    box-shadow: 0 3px 10px rgba(21, 101, 192, 0.25);
}}
.stButton > button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 5px 14px rgba(21, 101, 192, 0.35);
}}
.stButton > button:active {{
    transform: translateY(0);
}}

/* Botones secundarios */
div[data-testid="stButton"] > button[kind="secondary"] {{
    background: white;
    color: {THEME['primary']};
    border: 2px solid {THEME['primary']};
    box-shadow: none;
}}

/* ===== Inputs ===== */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {{
    border-radius: 10px !important;
    border: 2px solid {THEME['border']} !important;
    padding: 0.55rem 0.85rem !important;
    transition: border 0.2s ease;
}}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
    border-color: {THEME['primary']} !important;
    box-shadow: 0 0 0 3px rgba(21, 101, 192, 0.15) !important;
}}

/* ===== Alertas ===== */
.alert-success {{
    background: rgba(46, 125, 50, 0.10);
    border-left: 4px solid {THEME['success']};
    color: #1B5E20;
    padding: 0.85rem 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
}}
.alert-warning {{
    background: rgba(237, 108, 2, 0.10);
    border-left: 4px solid {THEME['warning']};
    color: #BF4F00;
    padding: 0.85rem 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
}}
.alert-danger {{
    background: rgba(198, 40, 40, 0.10);
    border-left: 4px solid {THEME['danger']};
    color: #B71C1C;
    padding: 0.85rem 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
}}
.alert-info {{
    background: rgba(21, 101, 192, 0.08);
    border-left: 4px solid {THEME['primary']};
    color: {THEME['primary_dark']};
    padding: 0.85rem 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
}}

/* ===== Crucigrama ===== */
.crossword-wrapper {{
    overflow-x: auto;
    padding: 0.5rem 0;
    -webkit-overflow-scrolling: touch;
}}
.crossword-grid {{
    display: grid;
    gap: 2px;
    background: {THEME['border']};
    padding: 2px;
    border-radius: 8px;
    width: max-content;
    margin: 0 auto;
}}
.cw-cell {{
    width: 38px;
    height: 38px;
    background: {THEME['bg_card']};
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
}}
.cw-cell.blocked {{
    background: transparent;
    visibility: hidden;
}}
.cw-cell input {{
    width: 100%;
    height: 100%;
    border: none;
    text-align: center;
    font-size: 1.05rem;
    font-weight: 600;
    color: {THEME['primary_dark']};
    background: {THEME['bg_card']};
    text-transform: uppercase;
}}
.cw-cell input:focus {{
    outline: 2px solid {THEME['primary']};
    outline-offset: -2px;
    background: rgba(21, 101, 192, 0.06);
}}
.cw-cell .num {{
    position: absolute;
    top: 1px;
    left: 2px;
    font-size: 0.55rem;
    color: {THEME['text_muted']};
    font-weight: 600;
    pointer-events: none;
    z-index: 2;
}}
.cw-cell.correct input {{
    color: {THEME['success']};
    background: rgba(46, 125, 50, 0.08);
}}
.cw-cell.incorrect input {{
    color: {THEME['danger']};
    background: rgba(198, 40, 40, 0.08);
}}

/* ===== Ruleta ===== */
.roulette-container {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
    padding: 1rem;
}}
.roulette-wheel {{
    width: 320px;
    height: 320px;
    border-radius: 50%;
    border: 8px solid {THEME['primary']};
    box-shadow: 0 8px 24px rgba(21, 101, 192, 0.3);
    transition: transform 4s cubic-bezier(0.17, 0.67, 0.12, 0.99);
    position: relative;
    background: conic-gradient(
        #1565C0 0deg 36deg,
        #2E7D32 36deg 72deg,
        #5E92F3 72deg 108deg,
        #66BB6A 108deg 144deg,
        #1565C0 144deg 180deg,
        #2E7D32 180deg 216deg,
        #5E92F3 216deg 252deg,
        #66BB6A 252deg 288deg,
        #1565C0 288deg 324deg,
        #2E7D32 324deg 360deg
    );
}}
.roulette-pointer {{
    width: 0;
    height: 0;
    border-left: 14px solid transparent;
    border-right: 14px solid transparent;
    border-top: 24px solid {THEME['warning']};
    position: absolute;
    top: -8px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 5;
}}
.winner-card {{
    background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
    border: 3px solid {THEME['warning']};
    border-radius: 18px;
    padding: 2rem;
    text-align: center;
    box-shadow: 0 8px 32px rgba(237, 108, 2, 0.25);
    margin-top: 1.5rem;
}}
.winner-card h2 {{
    margin: 0 0 0.5rem 0;
    color: #E65100;
    font-size: 1.8rem;
}}
.winner-card .info {{
    font-size: 1.05rem;
    color: #424242;
    margin: 0.25rem 0;
}}

/* ===== Tablas ===== */
.stDataFrame, .stTable {{
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px {THEME['shadow']};
}}
.stDataFrame table, .stTable table {{
    border-collapse: separate !important;
    border-spacing: 0;
}}
.stDataFrame thead th, .stTable thead th {{
    background: {THEME['primary']} !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 0.6rem 0.8rem !important;
}}
.stDataFrame tbody tr:nth-child(even), .stTable tbody tr:nth-child(even) {{
    background: #F5F7FA !important;
}}

/* ===== Badges y pills ===== */
.badge {{
    display: inline-block;
    padding: 0.25rem 0.7rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.3px;
}}
.badge-success {{ background: rgba(46, 125, 50, 0.15); color: #1B5E20; }}
.badge-warning {{ background: rgba(237, 108, 2, 0.15); color: #BF4F00; }}
.badge-danger {{ background: rgba(198, 40, 40, 0.15); color: #B71C1C; }}
.badge-info {{ background: rgba(21, 101, 192, 0.15); color: {THEME['primary_dark']}; }}

/* ===== Metric tiles ===== */
.metric-tile {{
    background: {THEME['bg_card']};
    border-radius: 14px;
    padding: 1rem 1.25rem;
    border: 1px solid {THEME['border']};
    box-shadow: 0 2px 8px {THEME['shadow']};
    text-align: center;
}}
.metric-tile .value {{
    font-size: 2rem;
    font-weight: 700;
    color: {THEME['primary']};
    line-height: 1.1;
}}
.metric-tile .label {{
    font-size: 0.8rem;
    color: {THEME['text_muted']};
    margin-top: 0.25rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* ===== Stepper (flujo del visitante) ===== */
.stepper {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 1rem 0 1.5rem 0;
    position: relative;
}}
.stepper::before {{
    content: '';
    position: absolute;
    top: 50%;
    left: 5%;
    right: 5%;
    height: 3px;
    background: {THEME['border']};
    z-index: 0;
}}
.step {{
    z-index: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.3rem;
}}
.step .dot {{
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: {THEME['border']};
    color: {THEME['text_muted']};
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    border: 3px solid {THEME['bg']};
}}
.step.active .dot {{
    background: {THEME['primary']};
    color: white;
    box-shadow: 0 0 0 4px rgba(21, 101, 192, 0.2);
}}
.step.done .dot {{
    background: {THEME['accent']};
    color: white;
}}
.step .label {{
    font-size: 0.75rem;
    color: {THEME['text_muted']};
    font-weight: 500;
}}
.step.active .label {{ color: {THEME['primary']}; font-weight: 600; }}

/* ===== Footer ===== */
.app-footer {{
    text-align: center;
    color: {THEME['text_muted']};
    font-size: 0.8rem;
    padding: 1.5rem 0 2rem 0;
    border-top: 1px solid {THEME['border']};
    margin-top: 2rem;
}}
.app-footer strong {{ color: {THEME['primary']}; }}

/* ===== Mobile responsive ===== */
@media (max-width: 768px) {{
    .app-header {{ flex-direction: column; text-align: center; gap: 0.75rem; padding: 1rem; }}
    .app-header img {{ height: 48px; }}
    .app-header .titles h1 {{ font-size: 1.15rem; }}
    .cw-cell {{ width: 32px; height: 32px; }}
    .cw-cell input {{ font-size: 0.9rem; }}
    .card {{ padding: 1rem; }}
    .roulette-wheel {{ width: 260px; height: 260px; }}
    .metric-tile .value {{ font-size: 1.5rem; }}
}}

/* ===== Hide Streamlit elements ===== */
#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
header[data-testid="stHeader"] {{ background: transparent; }}

/* ===== Consentimiento habeas data ===== */
.habeas-box {{
    background: rgba(21, 101, 192, 0.05);
    border: 1px solid {THEME['primary_light']};
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin: 1rem 0;
    font-size: 0.85rem;
    color: {THEME['text']};
    line-height: 1.55;
}}
</style>
"""


def render_header(subtitle: str = ""):
    """Renderiza el header institucional con logo y titulo."""
    import os
    import base64
    import streamlit as st

    # Cargar logo como data URI (funciona en Streamlit Cloud)
    logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              "assets", "logo.png")
    logo_uri = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_uri = "data:image/png;base64," + base64.b64encode(f.read()).decode()

    fallback = (
        f'<div style="display:flex; align-items:center; justify-content:center;'
        f'width:64px; height:64px; background:{THEME["primary"]}; color:white;'
        f'font-weight:700; font-size:1.4rem; border-radius:12px; padding:8px;">CSR</div>'
    )
    logo_html = (
        f'<img src="{logo_uri}" alt="Logo Clinica San Rafael" '
        f'style="height:64px; width:auto; background:white; padding:6px; border-radius:12px;" '
        f'onerror="this.style.display=\'none\'; this.nextElementSibling.style.display=\'flex\';">'
        f'<span style="display:none;"></span>'
        if logo_uri else fallback
    )
    html = f"""
    <div class="app-header">
        {logo_html}
        <div class="titles">
            <h1>Clinica San Rafael Alta Complejidad SAS</h1>
            <p>{subtitle or 'Semana SST - Sistema de Salud y Seguridad en el Trabajo'}</p>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_footer():
    """Renderiza el pie de pagina."""
    import streamlit as st
    st.markdown("""
    <div class="app-footer">
        <strong>Clinica San Rafael Alta Complejidad SAS</strong> &middot;
        Semana SST &middot; Sistema de Gestion SST Resolucion 0312/2019
    </div>
    """, unsafe_allow_html=True)


def render_stepper(steps: list, current: int):
    """Renderiza un stepper para el flujo del visitante.
    steps: lista de etiquetas, current: indice activo (0-based).
    """
    import streamlit as st
    html = '<div class="stepper">'
    for i, label in enumerate(steps):
        cls = "done" if i < current else ("active" if i == current else "")
        icon = "✓" if i < current else str(i + 1)
        html += f"""
        <div class="step {cls}">
            <div class="dot">{icon}</div>
            <div class="label">{label}</div>
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def inject_css():
    """Inyecta el CSS principal en la pagina."""
    import streamlit as st
    st.markdown(CSS, unsafe_allow_html=True)
