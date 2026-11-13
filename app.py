"""
APP PRINCIPAL - Semana SST - Clinica San Rafael Alta Complejidad SAS
====================================================================
Punto de entrada de Streamlit. Muestra landing estatica (sin conexion a BD)
con enlaces a las dos rutas: Visitante y Administrador.

El cronograma y el crucigrama solo se cargan dentro de la sesion del
visitante autenticado, no en la landing publica.

Ejecucion: streamlit run app.py
"""
from __future__ import annotations
import sys
import os

# Agregar la carpeta sst_app/ al path para imports directos.
_BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_BASE, "sst_app"))
sys.path.insert(0, _BASE)

import streamlit as st
import styles
from crucigrama_data import generar_resumen_visual


st.set_page_config(
    page_title="Semana SST - Clinica San Rafael",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

styles.inject_css()
styles.render_header("Bienvenidos a la Semana de Salud y Seguridad en el Trabajo")


# Cronograma estatico de ejemplo (no requiere conexion a BD)
# El administrador puede editarlo desde su panel, estos son los valores por defecto
CRONOGRAMA_ESTATICO = [
    {"dia": "2025-11-17", "hi": "08:00", "hf": "09:00",
     "actividad": "Inauguracion Semana SST",
     "desc": "Apertura oficial del evento y presentacion del cronograma",
     "responsable": "Comite SST", "ubicacion": "Auditorio principal"},
    {"dia": "2025-11-17", "hi": "09:00", "hf": "11:00",
     "actividad": "Capacitacion: SG-SST Resolucion 0312",
     "desc": "Recorrido por los estandares minimos del SG-SST",
     "responsable": "Coordinador SST", "ubicacion": "Auditorio principal"},
    {"dia": "2025-11-18", "hi": "10:00", "hf": "12:00",
     "actividad": "Taller de bioseguridad clinica",
     "desc": "Manejo de residuos hospitalarios y prevencion de pinchazos",
     "responsable": "Enfermeria EPS", "ubicacion": "Sala de capacitacion"},
    {"dia": "2025-11-19", "hi": "14:00", "hf": "16:00",
     "actividad": "Simulacro de evacuacion",
     "desc": "Practica de evacuacion y uso de extintores",
     "responsable": "Brigada de emergencias", "ubicacion": "Todas las sedes"},
    {"dia": "2025-11-20", "hi": "09:00", "hf": "11:00",
     "actividad": "Ergonomia en el puesto de trabajo",
     "desc": "Prevencion de lesiones musculo-esqueleticas",
     "responsable": "Fisioterapeuta", "ubicacion": "Sala multiusos"},
    {"dia": "2025-11-21", "hi": "15:00", "hf": "17:00",
     "actividad": "Cierre y sorteo del premio",
     "desc": "Entrega de reconocimientos y sorteo entre participantes",
     "responsable": "Direccion", "ubicacion": "Auditorio principal"},
]


def landing():
    """Pantalla principal estatica. No se conecta a Supabase.
    El cronograma y crucigrama solo se cargan en la sesion autenticada."""

    st.markdown("""
    <div class="card">
        <h2 class="card-title">🏥 Bienvenidos a la Semana SST</h2>
        <p style="font-size:1.05rem; color:#1A2332; line-height:1.6;">
            La <strong>Clinica San Rafael Alta Complejidad SAS</strong> da la bienvenida a todos
            los visitantes a la <strong>Semana de Salud y Seguridad en el Trabajo</strong>.
            Durante esta semana compartiremos conocimientos clave sobre bioseguridad,
            normativa SST colombiana y prevencion de riesgos laborales.
        </p>
        <p style="font-size:0.95rem; color:#5F6B7A;">
            Participa en nuestro <strong>crucigrama interactivo de 20 palabras SST</strong> y
            queda inscrito automaticamente en el sorteo del <strong>premio sorpresa</strong>
            que se realizara en la sesion de cierre del evento.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Botones de acceso
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="card" style="text-align:center; height:100%;">
            <div style="font-size:3rem; margin-bottom:0.5rem;">👤</div>
            <h3 style="color:#1565C0; margin:0 0 0.5rem 0;">Soy Visitante</h3>
            <p style="color:#5F6B7A; font-size:0.9rem; min-height:3rem;">
                Registra tus datos, valida tu correo y resuelve el crucigrama SST para participar.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("👉 Ingresar como Visitante", use_container_width=True, key="btn_visitante"):
            st.switch_page("pages/1_Visitante.py")

    with col2:
        st.markdown("""
        <div class="card" style="text-align:center; height:100%;">
            <div style="font-size:3rem; margin-bottom:0.5rem;">🔧</div>
            <h3 style="color:#1565C0; margin:0 0 0.5rem 0;">Soy Administrador</h3>
            <p style="color:#5F6B7A; font-size:0.9rem; min-height:3rem;">
                Acceso exclusivo para gestionar registros, historial y ruleta del premio.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("👉 Ingresar como Administrador", use_container_width=True,
                    key="btn_admin", type="primary"):
            st.switch_page("pages/2_Administrador.py")

    st.markdown("---")

    # Resumen del crucigrama (datos estaticos del layout, no requiere BD)
    resumen = generar_resumen_visual()
    st.markdown("""
    <div class="card">
        <h2 class="card-title">🧩 Actividad: Crucigrama SST</h2>
        <p style="color:#1A2332;">
            Pon a prueba tus conocimientos sobre salud y seguridad en el trabajo.
            Resuelve las 20 palabras para participar en el sorteo del premio sorpresa.
            El crucigrama se desbloquea una vez completes tu registro y valides tu correo.
        </p>
    </div>
    """, unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""<div class="metric-tile"><div class="value">{resumen['total_palabras']}</div>
                     <div class="label">Palabras</div></div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="metric-tile"><div class="value">{resumen['horizontales']}</div>
                     <div class="label">Horizontales</div></div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class="metric-tile"><div class="value">{resumen['verticales']}</div>
                     <div class="label">Verticales</div></div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""<div class="metric-tile"><div class="value">{resumen['total_letras']}</div>
                     <div class="label">Letras</div></div>""", unsafe_allow_html=True)

    # Cronograma estatico (no consulta a Supabase)
    st.markdown("---")
    st.markdown("""
    <div class="card">
        <h2 class="card-title">📅 Cronograma del Evento</h2>
        <p style="color:#5F6B7A; font-size:0.9rem; margin:0 0 0.5rem 0;">
            Agenda tentativa de la Semana SST.
        </p>
    </div>
    """, unsafe_allow_html=True)
    for item in CRONOGRAMA_ESTATICO:
        dia = item["dia"]
        hi = item["hi"]
        hf = item["hf"]
        actividad = item["actividad"]
        desc = item["desc"]
        responsable = item["responsable"]
        ubicacion = item["ubicacion"]
        st.markdown(f"""
        <div class="card" style="padding:1rem 1.25rem; margin-bottom:0.75rem;">
            <div style="display:flex; align-items:center; gap:1rem;">
                <div style="background:#1565C0; color:white; padding:0.5rem 0.85rem;
                            border-radius:10px; text-align:center; min-width:80px;">
                    <div style="font-size:0.7rem; opacity:0.9;">DIA</div>
                    <div style="font-size:1.1rem; font-weight:700;">{dia[-2:]}/{dia[5:7]}</div>
                </div>
                <div style="flex:1;">
                    <div style="font-weight:700; color:#1565C0; font-size:1rem;">{actividad}</div>
                    <div style="color:#5F6B7A; font-size:0.85rem;">⏰ {hi} - {hf} &middot; 📍 {ubicacion} &middot; 👤 {responsable}</div>
                    <div style="color:#1A2332; font-size:0.9rem; margin-top:0.3rem;">{desc}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Beneficios e info
    st.markdown("""
    <div class="card">
        <h2 class="card-title">🎁 Participa y Gana</h2>
        <p style="color:#1A2332; line-height:1.6;">
            Al completar el crucigrama con el 100% de aciertos quedas automaticamente
            inscrito en el <strong>sorteo del premio sorpresa</strong>. La ruleta se
            realizara en vivo durante la sesion de cierre del evento, ante todos
            los participantes, garantizando transparencia.
        </p>
        <p style="color:#5F6B7A; font-size:0.9rem; margin-top:1rem;">
            📋 Tratamiento de datos: La informacion registrada sera tratada conforme
            a la Ley 1581 de 2012 (Habeas Data) y solo se utilizara para fines del evento.
        </p>
    </div>
    """, unsafe_allow_html=True)

    styles.render_footer()


if __name__ == "__main__":
    landing()
