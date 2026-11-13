"""
PAGINA 2 - ADMINISTRADOR
========================
Panel de administracion:
  - Login usuario/contrasena
  - Dashboard con estadisticas del evento
  - CRUD de visitantes
  - Historial de accesos (bitacora)
  - Cronograma del evento (CRUD)
  - Ruleta del premio (sorteo en vivo)
  - Configuracion del evento
"""
from __future__ import annotations
import sys
import os
import secrets as pysecrets
import time
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from src import styles, database, auth, email_service
from src.crucigrama_data import generar_resumen_visual


st.set_page_config(
    page_title="Administrador - Semana SST",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

styles.inject_css()
styles.render_header("Panel de Administracion - Semana SST")


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
def pantalla_login():
    st.markdown("""
    <div class="card" style="max-width:480px; margin:2rem auto;">
        <h2 class="card-title">🔐 Acceso de Administrador</h2>
        <p class="card-subtitle">Ingresa tus credenciales para acceder al panel</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("form_login_admin"):
        usuario = st.text_input("Usuario")
        password = st.text_input("Contrasena", type="password")
        if st.form_submit_button("Ingresar", use_container_width=True, type="primary"):
            ok, msg = auth.login(usuario, password)
            if ok:
                st.success(msg)
                time.sleep(0.6)
                st.rerun()
            else:
                st.error(msg)

    st.markdown("""
    <div class="alert-info" style="max-width:480px; margin:1rem auto;">
        <strong>Primera vez?</strong> Ejecuta el script <code>crear_admin.py</code> para
        generar tu usuario administrador con un hash bcrypt valido.
    </div>
    """, unsafe_allow_html=True)

    if st.button("🏠 Volver al inicio"):
        st.switch_page("app.py")


# ---------------------------------------------------------------------------
# Menu lateral
# ---------------------------------------------------------------------------
def menu_lateral():
    admin = auth.get_current_admin()
    with st.sidebar:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg, #1565C0, #0D47A1);
                    color:white; padding:1rem; border-radius:12px; margin-bottom:1rem;">
            <div style="font-size:0.8rem; opacity:0.9;">Conectado como</div>
            <div style="font-weight:700; font-size:1rem;">{admin.get('nombre_completo', 'Admin')}</div>
            <div style="font-size:0.8rem; opacity:0.85; margin-top:0.25rem;">@{admin.get('usuario', '')}</div>
            <div style="display:inline-block; padding:0.15rem 0.5rem; background:rgba(255,255,255,0.2);
                        border-radius:6px; font-size:0.7rem; margin-top:0.5rem; text-transform:uppercase;">
                {admin.get('rol', 'admin')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        seccion = st.radio(
            "📍 Secciones",
            options=["📊 Dashboard", "👥 Visitantes (CRUD)", "📜 Historial accesos",
                     "📅 Cronograma", "🎡 Ruleta premio", "🏆 Ganadores",
                     "⚙️ Configuracion", "🔑 Cambiar contrasena"],
            index=0,
        )
        st.markdown("---")
        if st.button("🚪 Cerrar sesion", use_container_width=True):
            auth.logout()
            st.switch_page("app.py")
    return seccion


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
def seccion_dashboard():
    st.markdown('<h2 class="card-title">📊 Dashboard del Evento</h2>', unsafe_allow_html=True)
    try:
        stats = database.obtener_estadisticas()
        cronograma = database.listar_cronograma()
        sorteos = database.listar_sorteos()
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f"""<div class="metric-tile"><div class="value">{stats['total_registrados']}</div>
                     <div class="label">Registrados</div></div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="metric-tile"><div class="value">{stats['total_validados']}</div>
                     <div class="label">Email validados</div></div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class="metric-tile"><div class="value">{stats['total_crucigrama_ok']}</div>
                     <div class="label">Crucigrama OK</div></div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""<div class="metric-tile"><div class="value">{stats['total_habeas_data']}</div>
                     <div class="label">Habeas Data</div></div>""", unsafe_allow_html=True)
    with m5:
        st.markdown(f"""<div class="metric-tile"><div class="value">{stats['total_empresas']}</div>
                     <div class="label">Empresas</div></div>""", unsafe_allow_html=True)

    # Estado del premio
    st.markdown("---")
    st.markdown('<h3 style="color:#0D47A1;">🎡 Estado del Premio Sorpresa</h3>',
                unsafe_allow_html=True)
    try:
        premios = database.listar_premios()
        if premios:
            p = premios[0]
            estado = p.get("estado", "pendiente")
            badge_cls = {"pendiente": "badge-warning", "sorteado": "badge-success",
                         "entregado": "badge-info"}.get(estado, "badge-info")
            st.markdown(f"""
            <div class="card">
                <h4>{p.get('nombre', 'Premio sorpresa')}</h4>
                <p style="color:#5F6B7A;">{p.get('descripcion', '')}</p>
                <span class="badge {badge_cls}">{estado.upper()}</span>
                <span class="badge badge-info">{stats['total_crucigrama_ok']} participantes elegibles</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No hay premio configurado. Ve a Configuracion para crear uno.")
    except Exception:
        pass

    # Cronograma proximo
    st.markdown("---")
    st.markdown('<h3 style="color:#0D47A1;">📅 Proximas actividades</h3>',
                unsafe_allow_html=True)
    if cronograma:
        df = pd.DataFrame(cronograma)
        df["dia"] = pd.to_datetime(df["dia"]).dt.strftime("%Y-%m-%d")
        df_show = df[["dia", "hora_inicio", "hora_fin", "actividad", "ubicacion", "responsable"]]
        df_show.columns = ["Dia", "Inicio", "Fin", "Actividad", "Ubicacion", "Responsable"]
        st.dataframe(df_show, use_container_width=True, hide_index=True)
    else:
        st.info("No hay actividades programadas.")

    # Ultimos accesos
    st.markdown("---")
    st.markdown('<h3 style="color:#0D47A1;">📜 Ultimos accesos</h3>',
                unsafe_allow_html=True)
    try:
        accesos = database.listar_accesos(limit=10)
        if accesos:
            df = pd.DataFrame(accesos)
            df["creado_en"] = pd.to_datetime(df["creado_en"]).dt.strftime("%Y-%m-%d %H:%M")
            df_show = df[["creado_en", "tipo_usuario", "usuario_ref", "accion", "exitoso"]]
            df_show.columns = ["Fecha", "Tipo", "Usuario", "Accion", "OK"]
            st.dataframe(df_show, use_container_width=True, hide_index=True)
        else:
            st.info("Sin accesos registrados.")
    except Exception as e:
        st.error(f"Error: {e}")


# ---------------------------------------------------------------------------
# CRUD Visitantes
# ---------------------------------------------------------------------------
def seccion_visitantes_crud():
    st.markdown('<h2 class="card-title">👥 Visitantes (CRUD)</h2>', unsafe_allow_html=True)
    try:
        visitantes = database.listar_visitantes(limit=1000)
    except Exception as e:
        st.error(f"Error cargando visitantes: {e}")
        return

    if not visitantes:
        st.info("No hay visitantes registrados.")
        return

    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        buscar = st.text_input("🔎 Buscar (nombre, cedula, correo, empresa)", "")
    with col2:
        filtro_estado = st.selectbox("Estado email", ["Todos", "Validados", "No validados"])
    with col3:
        filtro_crucigrama = st.selectbox("Crucigrama", ["Todos", "Completados", "No completados"])

    df = pd.DataFrame(visitantes)
    df["creado_en"] = pd.to_datetime(df["creado_en"]).dt.strftime("%Y-%m-%d %H:%M")
    if buscar:
        mask = df.apply(lambda r: buscar.lower() in str(r.get("nombre", "")).lower() +
                        str(r.get("cedula", "")).lower() +
                        str(r.get("correo", "")).lower() +
                        str(r.get("empresa", "")).lower(), axis=1)
        df = df[mask]
    if filtro_estado == "Validados":
        df = df[df["email_validado"] == True]
    elif filtro_estado == "No validados":
        df = df[df["email_validado"] == False]
    if filtro_crucigrama == "Completados":
        df = df[df["crucigrama_completado"] == True]
    elif filtro_crucigrama == "No completados":
        df = df[df["crucigrama_completado"] == False]

    st.markdown(f"**{len(df)}** registro(s) encontrado(s)")

    df_show = df[["id", "cedula", "nombre", "cargo", "correo", "telefono", "empresa",
                   "habeas_data", "email_validado", "crucigrama_completado",
                   "crucigrama_puntaje", "creado_en"]]
    df_show.columns = ["ID", "Cedula", "Nombre", "Cargo", "Correo", "Telefono",
                       "Empresa", "Habeas", "Email OK", "Crucigrama", "Puntaje", "Creado"]
    st.dataframe(df_show, use_container_width=True, hide_index=True)

    # Operaciones
    st.markdown("---")
    st.markdown('<h3 style="color:#0D47A1;">Operaciones</h3>', unsafe_allow_html=True)
    op = st.radio("Selecciona accion", ["Editar", "Eliminar", "Marcar crucigrama completado"],
                  horizontal=True, label_visibility="collapsed")

    ids = df["id"].tolist()
    opciones = [f"{r['cedula']} - {r['nombre']}" for _, r in df.iterrows()]
    if not opciones:
        st.info("No hay registros para operar.")
        return
    seleccion = st.selectbox("Selecciona visitante", opciones)
    idx = opciones.index(seleccion)
    visitante_sel = df.iloc[idx].to_dict()

    if op == "Editar":
        _form_editar_visitante(visitante_sel)
    elif op == "Eliminar":
        _confirmar_eliminar(visitante_sel)
    elif op == "Marcar crucigrama completado":
        _marcar_crucigrama(visitante_sel)


def _form_editar_visitante(v: dict):
    st.markdown(f"""
    <div class="card">
        <h4 style="color:#1565C0; margin-top:0;">Editar visitante: {v.get('nombre','')}</h4>
    </div>
    """, unsafe_allow_html=True)
    with st.form("form_edit_visitante"):
        col1, col2 = st.columns(2)
        with col1:
            cedula = st.text_input("Cedula", value=v.get("cedula", ""))
            nombre = st.text_input("Nombre", value=v.get("nombre", ""))
            cargo = st.text_input("Cargo", value=v.get("cargo", ""))
            telefono = st.text_input("Telefono", value=v.get("telefono", "") or "")
        with col2:
            correo = st.text_input("Correo", value=v.get("correo", ""))
            empresa = st.text_input("Empresa", value=v.get("empresa", ""))
            habeas = st.checkbox("Habeas data aceptado",
                                  value=bool(v.get("habeas_data", False)))
            email_ok = st.checkbox("Email validado",
                                    value=bool(v.get("email_validado", False)))
        cruc_ok = st.checkbox("Crucigrama completado",
                              value=bool(v.get("crucigrama_completado", False)))
        puntaje = st.slider("Puntaje crucigrama (%)", 0, 100,
                             int(v.get("crucigrama_puntaje") or 0))
        if st.form_submit_button("Guardar cambios", type="primary"):
            try:
                database.actualizar_visitante(v["id"], {
                    "cedula": cedula.strip(),
                    "nombre": nombre.strip().upper(),
                    "cargo": cargo.strip(),
                    "correo": correo.strip().lower(),
                    "telefono": telefono.strip() or None,
                    "empresa": empresa.strip(),
                    "habeas_data": habeas,
                    "email_validado": email_ok,
                    "crucigrama_completado": cruc_ok,
                    "crucigrama_puntaje": puntaje,
                })
                database.registrar_acceso("admin",
                                            auth.get_current_admin().get("usuario", ""),
                                            "edit_visitante", detalle=v["id"],
                                            exitoso=True)
                st.success("Cambios guardados correctamente.")
                time.sleep(0.8)
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")


def _confirmar_eliminar(v: dict):
    st.warning(f"Vas a eliminar a {v.get('nombre', '')} (cedula {v.get('cedula', '')}). "
               "Esta accion no se puede deshacer.")
    if st.button("🗑️ Confirmar eliminacion", type="primary"):
        try:
            database.eliminar_visitante(v["id"])
            database.registrar_acceso("admin", auth.get_current_admin().get("usuario", ""),
                                       "delete_visitante",
                                       detalle=v.get("cedula", ""), exitoso=True)
            st.success("Visitante eliminado.")
            time.sleep(0.8)
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")


def _marcar_crucigrama(v: dict):
    if v.get("crucigrama_completado"):
        st.info("Este visitante ya tiene el crucigrama completado.")
    else:
        if st.button("✅ Marcar como completado (100%)"):
            try:
                database.actualizar_visitante(v["id"], {
                    "crucigrama_completado": True,
                    "crucigrama_puntaje": 100,
                    "crucigrama_resuelto_en": datetime.now().isoformat(),
                })
                database.registrar_acceso("admin",
                                           auth.get_current_admin().get("usuario", ""),
                                           "mark_crucigrama_ok", detalle=v["id"],
                                           exitoso=True)
                st.success("Marcado como completado.")
                time.sleep(0.8)
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")


# ---------------------------------------------------------------------------
# Historial de accesos
# ---------------------------------------------------------------------------
def seccion_historial():
    st.markdown('<h2 class="card-title">📜 Historial de Accesos</h2>',
                unsafe_allow_html=True)
    try:
        accesos = database.listar_accesos(limit=500)
    except Exception as e:
        st.error(f"Error: {e}")
        return
    if not accesos:
        st.info("Sin accesos registrados.")
        return

    df = pd.DataFrame(accesos)
    df["creado_en"] = pd.to_datetime(df["creado_en"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    df = df.sort_values("creado_en", ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        tipos = ["Todos"] + list(df["tipo_usuario"].unique())
        f_tipo = st.selectbox("Filtrar por tipo", tipos)
    with col2:
        descarga = st.checkbox("Descargar como CSV")

    if f_tipo != "Todos":
        df = df[df["tipo_usuario"] == f_tipo]

    df_show = df[["creado_en", "tipo_usuario", "usuario_ref", "correo",
                   "accion", "detalle", "exitoso", "ip_origen"]]
    df_show.columns = ["Fecha", "Tipo", "Usuario", "Correo", "Accion",
                        "Detalle", "OK", "IP"]
    st.dataframe(df_show, use_container_width=True, hide_index=True)

    if descarga:
        csv = df_show.to_csv(index=False).encode("utf-8")
        st.download_button("Descargar CSV", csv,
                            file_name=f"historial_accesos_{date.today()}.csv",
                            mime="text/csv")


# ---------------------------------------------------------------------------
# Cronograma CRUD
# ---------------------------------------------------------------------------
def seccion_cronograma():
    st.markdown('<h2 class="card-title">📅 Cronograma del Evento (CRUD)</h2>',
                unsafe_allow_html=True)
    try:
        items = database.listar_cronograma()
    except Exception as e:
        st.error(f"Error: {e}")
        return

    if items:
        df = pd.DataFrame(items)
        df["dia"] = pd.to_datetime(df["dia"]).dt.strftime("%Y-%m-%d")
        st.dataframe(df[["dia", "hora_inicio", "hora_fin", "actividad",
                         "descripcion", "responsable", "ubicacion"]],
                      use_container_width=True, hide_index=True)
    else:
        st.info("No hay actividades. Agrega una nueva abajo.")

    st.markdown("---")
    st.markdown('<h3 style="color:#0D47A1;">Agregar / Editar actividad</h3>',
                unsafe_allow_html=True)
    with st.form("form_cronograma"):
        col1, col2, col3 = st.columns(3)
        with col1:
            dia = st.date_input("Dia", value=date.today())
            hi = st.time_input("Hora inicio", value=time(8, 0))
        with col2:
            hf = st.time_input("Hora fin", value=time(10, 0))
            ubicacion = st.text_input("Ubicacion", "")
        with col3:
            responsable = st.text_input("Responsable", "")
            actividad = st.text_input("Actividad *", "")
        descripcion = st.text_area("Descripcion")
        if st.form_submit_button("Agregar actividad", type="primary"):
            if not actividad:
                st.error("La actividad es obligatoria.")
            else:
                try:
                    database.crear_cronograma({
                        "dia": dia.isoformat(),
                        "hora_inicio": hi.strftime("%H:%M:%S"),
                        "hora_fin": hf.strftime("%H:%M:%S"),
                        "actividad": actividad,
                        "descripcion": descripcion,
                        "responsable": responsable,
                        "ubicacion": ubicacion,
                    })
                    st.success("Actividad agregada.")
                    time.sleep(0.6)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    # Eliminar
    if items:
        st.markdown("---")
        st.markdown('<h4 style="color:#C62828;">Eliminar actividad</h4>',
                    unsafe_allow_html=True)
        sel = st.selectbox("Actividad a eliminar",
                            [f"{it['dia']} | {it['actividad']}" for it in items])
        if st.button("🗑️ Eliminar seleccionada"):
            idx = [f"{it['dia']} | {it['actividad']}" for it in items].index(sel)
            try:
                database.eliminar_cronograma(items[idx]["id"])
                st.success("Actividad eliminada.")
                time.sleep(0.6)
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")


# ---------------------------------------------------------------------------
# Ruleta del premio
# ---------------------------------------------------------------------------
def seccion_ruleta():
    st.markdown('<h2 class="card-title">🎡 Ruleta del Premio Sorpresa</h2>',
                unsafe_allow_html=True)
    admin = auth.get_current_admin()
    try:
        participantes = database.listar_participantes_ruleta()
        premios = database.listar_premios()
        sorteos = database.listar_sorteos()
    except Exception as e:
        st.error(f"Error: {e}")
        return

    # Si ya hay sorteo
    if sorteos:
        st.markdown('<h3 style="color:#2E7D32;">🏆 Ultimo sorteo realizado</h3>',
                    unsafe_allow_html=True)
        ultimo = sorteos[0]
        ganador_id = ultimo.get("ganador_id")
        ganador = None
        if ganador_id:
            ganador = database.obtener_visitante(ganador_id)
        if ganador:
            st.markdown(f"""
            <div class="winner-card">
                <h2>🎉 ¡GANADOR!</h2>
                <div class="info"><strong>{ganador.get('nombre','')}</strong></div>
                <div class="info">Cedula: {ganador.get('cedula','')}</div>
                <div class="info">Cargo: {ganador.get('cargo','')}</div>
                <div class="info">Empresa: {ganador.get('empresa','')}</div>
                <div class="info">Correo: {ganador.get('correo','')}</div>
                <div class="info" style="margin-top:1rem; font-size:0.85rem; color:#666;">
                    Sorteo ejecutado: {ultimo.get('ejecutado_en','')[:19]} |
                    Participantes: {ultimo.get('participantes_total',0)} |
                    Semilla: {ultimo.get('semilla','')}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Sorteo registrado pero el ganador ya no esta disponible.")

        if st.button("🔄 Realizar nuevo sorteo", use_container_width=True):
            if not participantes:
                st.warning("No hay participantes elegibles.")
            else:
                _ejecutar_sorteo(participantes, premios, admin)
        return

    # Sin sorteo previo
    st.markdown(f"""
    <div class="alert-info">
        <strong>Participantes elegibles:</strong> {len(participantes)} visitante(s) que
        completaron el crucigrama al 100% con correo validado y habeas data aceptado.
    </div>
    """, unsafe_allow_html=True)

    if not participantes:
        st.warning("Aun no hay participantes elegibles para el sorteo.")
        return

    # Mostrar lista de participantes
    with st.expander(f"Ver {len(participantes)} participantes elegibles"):
        df = pd.DataFrame(participantes)
        df_show = df[["cedula", "nombre", "cargo", "empresa", "crucigrama_puntaje"]]
        df_show.columns = ["Cedula", "Nombre", "Cargo", "Empresa", "Puntaje"]
        st.dataframe(df_show, use_container_width=True, hide_index=True)

    # Ruleta visual
    st.markdown("""
    <div class="roulette-container">
        <div style="position:relative;">
            <div class="roulette-pointer"></div>
            <div class="roulette-wheel" id="wheel"></div>
        </div>
        <p style="color:#5F6B7A; font-size:0.9rem; text-align:center; max-width:400px;">
            Presiona el boton para ejecutar el sorteo aleatorio frente a todos.
            La seleccion es transparente y reproducible (semilla registrada).
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🎲 Ejecutar sorteo en vivo", type="primary", use_container_width=True):
        _ejecutar_sorteo(participantes, premios, admin)


def _ejecutar_sorteo(participantes: list, premios: list, admin: dict):
    """Ejecuta el sorteo con semilla aleatoria y guarda el resultado."""
    if not participantes:
        st.warning("No hay participantes.")
        return
    if not premios:
        st.error("No hay premio configurado.")
        return

    premio = premios[0]
    semilla = pysecrets.token_hex(16)
    # Seleccion aleatoria usando la semilla
    import random
    rng = random.Random(semilla)
    ganador = rng.choice(participantes)

    # Animacion visual (solo cosmetic)
    st.markdown("""
    <script>
        document.getElementById('wheel').style.transform = 'rotate(1440deg)';
    </script>
    """, unsafe_allow_html=True)

    # Guardar sorteo
    try:
        database.guardar_sorteo(
            premio_id=premio["id"],
            admin_id=admin["id"],
            participantes_total=len(participantes),
            ganador_id=ganador["id"],
            semilla=semilla,
        )
        database.registrar_acceso("admin", admin.get("usuario", ""), "sorteo_ejecutado",
                                   detalle=f"ganador: {ganador.get('cedula','')} | "
                                           f"participantes: {len(participantes)}",
                                   exitoso=True)
        # Notificar al ganador por correo (no bloqueante)
        try:
            email_service.enviar_notificacion_ganador(
                ganador.get("correo", ""),
                ganador.get("nombre", ""),
                premio.get("nombre", "Premio sorpresa"),
            )
        except Exception:
            pass
    except Exception as e:
        st.error(f"Error guardando sorteo: {e}")
        return

    # Mostrar resultado
    st.balloons()
    st.markdown(f"""
    <div class="winner-card">
        <h2>🎉 ¡GANADOR!</h2>
        <div class="info"><strong>{ganador.get('nombre','')}</strong></div>
        <div class="info">Cedula: {ganador.get('cedula','')}</div>
        <div class="info">Cargo: {ganador.get('cargo','')}</div>
        <div class="info">Empresa: {ganador.get('empresa','')}</div>
        <div class="info">Correo: {ganador.get('correo','')}</div>
        <div class="info" style="margin-top:1rem; font-size:0.85rem; color:#666;">
            Total participantes: {len(participantes)} &middot;
            Semilla: <code>{semilla[:8]}...</code>
        </div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(1.5)
    st.rerun()


# ---------------------------------------------------------------------------
# Ganadores historicos
# ---------------------------------------------------------------------------
def seccion_ganadores():
    st.markdown('<h2 class="card-title">🏆 Historial de Ganadores</h2>',
                unsafe_allow_html=True)
    try:
        sorteos = database.listar_sorteos()
    except Exception as e:
        st.error(f"Error: {e}")
        return
    if not sorteos:
        st.info("Aun no se han realizado sorteos.")
        return
    rows = []
    for s in sorteos:
        ganador = database.obtener_visitante(s["ganador_id"]) if s.get("ganador_id") else None
        rows.append({
            "Fecha": s.get("ejecutado_en", "")[:19],
            "Ganador": ganador.get("nombre", "") if ganador else "(no disponible)",
            "Cedula": ganador.get("cedula", "") if ganador else "",
            "Empresa": ganador.get("empresa", "") if ganador else "",
            "Participantes": s.get("participantes_total", 0),
            "Semilla": s.get("semilla", "")[:12] + "...",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# Configuracion
# ---------------------------------------------------------------------------
def seccion_configuracion():
    st.markdown('<h2 class="card-title">⚙️ Configuracion del Evento</h2>',
                unsafe_allow_html=True)
    try:
        config = database.obtener_configuracion()
    except Exception as e:
        st.error(f"Error: {e}")
        return

    with st.form("form_config"):
        col1, col2 = st.columns(2)
        with col1:
            evento_nombre = st.text_input("Nombre del evento",
                                           value=config.get("evento_nombre", "Semana SST"))
            fecha_inicio = st.date_input("Fecha inicio",
                                          value=date.fromisoformat(config.get("evento_fecha_inicio", "2025-11-17")))
            fecha_fin = st.date_input("Fecha fin",
                                       value=date.fromisoformat(config.get("evento_fecha_fin", "2025-11-21")))
        with col2:
            premio_desc = st.text_input("Descripcion del premio",
                                          value=config.get("premio_descripcion", ""))
            intentos_max = st.number_input("Intentos maximos crucigrama",
                                            min_value=1, max_value=10,
                                            value=int(config.get("crucigrama_intentos_maximos", "3") or 3))
            validez_2fa = st.number_input("Validez codigo 2FA (minutos)",
                                            min_value=5, max_value=60,
                                            value=int(config.get("2fa_validez_minutos", "10") or 10))
        if st.form_submit_button("Guardar configuracion", type="primary"):
            try:
                database.actualizar_configuracion("evento_nombre", evento_nombre)
                database.actualizar_configuracion("evento_fecha_inicio", fecha_inicio.isoformat())
                database.actualizar_configuracion("evento_fecha_fin", fecha_fin.isoformat())
                database.actualizar_configuracion("premio_descripcion", premio_desc)
                database.actualizar_configuracion("crucigrama_intentos_maximos", str(intentos_max))
                database.actualizar_configuracion("2fa_validez_minutos", str(validez_2fa))
                st.success("Configuracion guardada.")
                time.sleep(0.6)
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    # Crear premio si no existe
    st.markdown("---")
    st.markdown('<h3 style="color:#0D47A1;">Gestion de premios</h3>', unsafe_allow_html=True)
    try:
        premios = database.listar_premios()
    except Exception as e:
        st.error(f"Error: {e}")
        return

    if premios:
        for p in premios:
            with st.expander(f"Premio: {p.get('nombre','')} ({p.get('estado','')})"):
                with st.form(f"form_premio_{p['id']}"):
                    nombre = st.text_input("Nombre", value=p.get("nombre", ""))
                    descripcion = st.text_area("Descripcion",
                                                value=p.get("descripcion", "") or "")
                    estado = st.selectbox("Estado", ["pendiente", "sorteado", "entregado"],
                                           index=["pendiente", "sorteado", "entregado"].index(p.get("estado", "pendiente")))
                    if st.form_submit_button("Actualizar premio"):
                        try:
                            database.actualizar_premio(p["id"], {
                                "nombre": nombre, "descripcion": descripcion, "estado": estado,
                            })
                            st.success("Premio actualizado.")
                            time.sleep(0.6)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
    else:
        st.info("No hay premios configurados. Crea uno:")
        with st.form("form_crear_premio"):
            nombre = st.text_input("Nombre del premio *")
            descripcion = st.text_area("Descripcion")
            if st.form_submit_button("Crear premio", type="primary"):
                if not nombre:
                    st.error("El nombre es obligatorio.")
                else:
                    try:
                        database.get_client().table("sst_premios").insert({
                            "nombre": nombre, "descripcion": descripcion, "estado": "pendiente",
                        }).execute()
                        st.success("Premio creado.")
                        time.sleep(0.6)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")


# ---------------------------------------------------------------------------
# Cambiar contrasena
# ---------------------------------------------------------------------------
def seccion_password():
    st.markdown('<h2 class="card-title">🔑 Cambiar mi contrasena</h2>',
                unsafe_allow_html=True)
    admin = auth.get_current_admin()
    with st.form("form_password"):
        actual = st.text_input("Contrasena actual", type="password")
        nueva = st.text_input("Nueva contrasena", type="password")
        confirmar = st.text_input("Confirmar nueva contrasena", type="password")
        if st.form_submit_button("Cambiar contrasena", type="primary"):
            if nueva != confirmar:
                st.error("Las contrasenas nuevas no coinciden.")
                return
            ok, msg = auth.cambiar_password(admin.get("usuario", ""), actual, nueva)
            if ok:
                st.success(msg)
            else:
                st.error(msg)


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
def main():
    if not auth.is_logged_in():
        pantalla_login()
        styles.render_footer()
        return

    seccion = menu_lateral()
    if "Dashboard" in seccion:
        seccion_dashboard()
    elif "Visitantes" in seccion:
        seccion_visitantes_crud()
    elif "Historial" in seccion:
        seccion_historial()
    elif "Cronograma" in seccion:
        seccion_cronograma()
    elif "Ruleta" in seccion:
        seccion_ruleta()
    elif "Ganadores" in seccion:
        seccion_ganadores()
    elif "Configuracion" in seccion:
        seccion_configuracion()
    elif "Contrasena" in seccion:
        seccion_password()
    styles.render_footer()


if __name__ == "__main__":
    main()
