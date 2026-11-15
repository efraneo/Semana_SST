"""
APP PRINCIPAL - Semana SST - Clinica San Rafael Alta Complejidad SAS
====================================================================
Punto de entrada de Streamlit. Muestra landing estatica (sin conexion a BD)
con enlaces a las dos rutas: Visitante y Administrador.

El crucigrama solo se carga dentro de la sesion del visitante autenticado.
El cronograma de actividades se visualiza mediante Genially (enlace externo).

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


# Configuracion del evento
EVENTO_FECHA_INICIO = "17 de noviembre de 2025"
EVENTO_FECHA_FIN = "20 de noviembre de 2025"
GENIALLY_URL = "https://view.genially.com/6af5dedaba8b594cb3b61fec"


def landing():
    """Pantalla principal estatica. No se conecta a Supabase.
    El crucigrama solo se carga en la sesion autenticada del visitante."""

    st.markdown(f"""
    <div class="card">
        <h2 class="card-title">🏥 Bienvenidos a la Semana SST</h2>
        <p style="font-size:1.05rem; color:#1A2332; line-height:1.6;">
            La <strong>Clinica San Rafael Alta Complejidad SAS</strong> da la bienvenida a todos
            los visitantes a la <strong>Semana de Salud y Seguridad en el Trabajo</strong>,
            que se desarrollara del <strong>{EVENTO_FECHA_INICIO}</strong> al
            <strong>{EVENTO_FECHA_FIN}</strong>. Durante esta semana compartiremos conocimientos
            clave sobre bioseguridad, normativa SST colombiana y prevencion de riesgos laborales.
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

    # Cronograma de actividades (Genially)
    st.markdown("---")
    st.markdown("""
    <div class="card">
        <h2 class="card-title">📅 Cronograma de Actividades</h2>
        <p style="color:#1A2332;">
            Consulta la agenda completa de la Semana SST con todos los detalles de
            cada actividad, responsables y ubicaciones en nuestra presentacion interactiva.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div style="text-align:center; margin:1.5rem 0;">
        <a href="{GENIALLY_URL}" target="_blank" rel="noopener noreferrer"
           style="display:inline-block; padding:0.85rem 2rem;
                  background:linear-gradient(135deg, #1565C0 0%, #0D47A1 100%);
                  color:white; text-decoration:none; font-weight:600;
                  border-radius:10px; box-shadow:0 4px 14px rgba(21,101,192,0.30);
                  transition:all 0.2s ease;">
            🎨 Ver cronograma interactivo (Genially)
        </a>
        <p style="color:#5F6B7A; font-size:0.85rem; margin-top:0.85rem;">
            Se abrira en una nueva pestana
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Iframe embebido del Genially (vista previa)
    st.markdown("""
    <div class="card" style="padding:0.5rem;">
        <h4 style="color:#0D47A1; margin:0.5rem 0; text-align:center;">
            🖼️ Vista previa del cronograma
        </h4>
    </div>
    """, unsafe_allow_html=True)
    st.components.v1.iframe(GENIALLY_URL, height=600, scrolling=True)

    # Beneficios e info
    st.markdown("""
    <div class="card">
        <h2 class="card-title">🎁 Participa y Gana</h2>
        <p style="color:#1A2332; line-height:1.6;">
            Al completar el crucigrama con el 100% de aciertos quedas automaticamente
            inscrito en el <strong>sorteo del premio sorpresa</strong>. La ruleta se
            realizara en vivo durante la sesion de cierre del evento el
            <strong>20 de noviembre de 2025</strong>, ante todos los participantes,
            garantizando transparencia.
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
