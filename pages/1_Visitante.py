"""
PAGINA 1 - VISITANTE
====================
Flujo completo del visitante:
  Paso 1: Registro de datos personales + consentimiento habeas data
  Paso 2: Validacion 2FA via correo electronico
  Paso 3: Resolucion del crucigrama SST (20 palabras)
"""
from __future__ import annotations
import sys
import os
import time
import re
from datetime import datetime, timezone

# Agregar la carpeta sst_app/ al path para imports directos
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_BASE, "sst_app"))
sys.path.insert(0, _BASE)

import streamlit as st
import styles
import database
import email_service
import auth
import crucigrama_data as cw


st.set_page_config(
    page_title="Visitante - Semana SST",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="collapsed",
)

styles.inject_css()
styles.render_header("Registro de Visitante - Semana SST")


# ---------------------------------------------------------------------------
# Estado de sesion
# ---------------------------------------------------------------------------
def init_state():
    s = st.session_state
    defaults = {
        "visitante_paso": 1,        # 1:registro, 2:2FA, 3:crucigrama, 4:finalizado
        "visitante_id": None,
        "visitante_nombre": "",
        "visitante_correo": "",
        "2fa_codigo_id": None,
        "2fa_intentos": 0,
        "2fa_reenviado_en": 0,
        "crucigrama_respuestas": {},
        "crucigrama_inicio": None,
    }
    for k, v in defaults.items():
        if k not in s:
            s[k] = v


init_state()


def validar_correo(correo: str) -> bool:
    patron = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(patron, correo) is not None


def validar_cedula(cedula: str) -> bool:
    """Valida cedula colombiana: 6-12 digitos numericos."""
    return bool(re.match(r"^\d{6,12}$", str(cedula).strip()))


# ---------------------------------------------------------------------------
# PASO 1: Registro
# ---------------------------------------------------------------------------
def paso_registro():
    st.markdown('<h2 class="card-title">📝 Paso 1: Registro del Visitante</h2>',
                unsafe_allow_html=True)
    styles.render_stepper(["Registro", "Verificacion", "Crucigrama", "Listo"], 0)

    st.markdown("""
    <div class="alert-info">
        Completa tus datos personales para iniciar el registro en la Semana SST.
        Te enviaremos un codigo de verificacion a tu correo.
    </div>
    """, unsafe_allow_html=True)

    with st.form("form_registro", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            cedula = st.text_input("Numero de cedula *", max_chars=12,
                                    help="Entre 6 y 12 digitos, sin puntos ni espacios.")
            nombre = st.text_input("Nombre completo *", max_chars=120,
                                    help="Nombres y apellidos completos.")
            cargo = st.text_input("Cargo / Rol *", max_chars=80,
                                   help="Tu cargo actual o rol en la empresa.")
        with col2:
            correo = st.text_input("Correo electronico *", max_chars=120,
                                    help="Correo donde recibiras el codigo 2FA.",
                                    placeholder="ejemplo@dominio.com")
            telefono = st.text_input("Telefono celular (opcional)", max_chars=20,
                                       help="Solo digitos y el simbolo +.")
            empresa = st.text_input("Empresa / Institucion *", max_chars=120,
                                     help="Empresa o institucion a la que perteneces.")

        # Habeas data
        st.markdown("""
        <div class="habeas-box">
            <strong>AUTORIZACION PARA EL TRATAMIENTO DE DATOS PERSONALES (HABEAS DATA)</strong><br><br>
            De conformidad con la Ley 1581 de 2012, el Decreto 1377 de 2013 y la
            Politica de Tratamiento de Datos Personales de la <strong>Clinica San Rafael
            Alta Complejidad SAS</strong>, autorizo de manera libre, previa, expresa,
            voluntaria e inequívoca a la Clinica para que recolecte, almacene, use,
            circule y trate mis datos personales con la finalidad de: (i) registrar mi
            participacion en la Semana SST, (ii) realizar el seguimiento a las
            actividades del evento, (iii) contactarme para fines relacionados con el
            evento y la divulgacion de contenido SST, y (iv) registrar el resultado de
            mi actividad en el crucigrama y mi participacion en el sorteo del premio.
            <br><br>
            Entiendo que como titular de los datos tengo derecho a conocer, actualizar,
            rectificar y suprimir mi informacion personal. Esta autorizacion se otorga
            por el termino de duracion del evento y mientras se cumplan las finalidades
            descritas.
        </div>
        """, unsafe_allow_html=True)
        habeas = st.checkbox("Acepto la autorizacion para el tratamiento de mis datos personales.",
                            value=False, key="habeas_chk")
        enviar = st.form_submit_button("Continuar", use_container_width=True, type="primary")

    if enviar:
        errores = []
        if not validar_cedula(cedula):
            errores.append("La cedula debe tener entre 6 y 12 digitos numericos.")
        if not nombre.strip():
            errores.append("El nombre es obligatorio.")
        if not cargo.strip():
            errores.append("El cargo es obligatorio.")
        if not validar_correo(correo):
            errores.append("El correo electronico no es valido.")
        if not empresa.strip():
            errores.append("La empresa es obligatoria.")
        if not habeas:
            errores.append("Debes aceptar la autorizacion de habeas data para continuar.")

        # Verificar duplicados
        if validar_cedula(cedula):
            try:
                if database.buscar_visitante_por_cedula(cedula):
                    errores.append("Ya existe un registro con esta cedula.")
            except Exception:
                pass
        if validar_correo(correo):
            try:
                if database.buscar_visitante_por_correo(correo):
                    errores.append("Ya existe un registro con este correo.")
            except Exception:
                pass

        if errores:
            for e in errores:
                st.error(e)
            return

        # Guardar visitante
        try:
            visitante = database.crear_visitante({
                "cedula": cedula, "nombre": nombre, "cargo": cargo,
                "correo": correo, "telefono": telefono, "empresa": empresa,
                "habeas_data": True,
            })
        except Exception as e:
            st.error(f"Error al registrar: {e}")
            return

        st.session_state.visitante_id = visitante["id"]
        st.session_state.visitante_nombre = nombre.upper()
        st.session_state.visitante_correo = correo.strip().lower()
        st.session_state.visitante_paso = 2

        # Bitacora
        database.registrar_acceso("visitante", cedula, "registro_visitante",
                                  correo=correo, exitoso=True)
        st.rerun()


# ---------------------------------------------------------------------------
# PASO 2: Verificacion 2FA
# ---------------------------------------------------------------------------
def paso_2fa():
    st.markdown('<h2 class="card-title">🔐 Paso 2: Verificacion por Correo</h2>',
                unsafe_allow_html=True)
    styles.render_stepper(["Registro", "Verificacion", "Crucigrama", "Listo"], 1)

    st.markdown(f"""
    <div class="alert-info">
        Hemos enviado un codigo de verificacion de 6 digitos a:
        <strong>{st.session_state.visitante_correo}</strong><br>
        Ingresa el codigo a continuacion. El codigo es valido por 10 minutos.
    </div>
    """, unsafe_allow_html=True)

    # Enviar codigo automaticamente la primera vez
    if st.session_state["2fa_codigo_id"] is None:
        try:
            _enviar_codigo_2fa()
        except Exception as e:
            st.error(f"Error enviando codigo 2FA: {e}")
            st.info("Verifica que las credenciales SMTP esten configuradas correctamente.")
            if st.button("Reintentar envio"):
                st.rerun()
            return

    codigo_ingresado = st.text_input("Codigo de verificacion (6 digitos)",
                                       max_chars=6, placeholder="000000")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Validar codigo", use_container_width=True, type="primary"):
            _validar_2fa(codigo_ingresado)
    with col2:
        # Reenvio con cooldown de 60s
        elapsed = time.time() - st.session_state["2fa_reenviado_en"]
        if elapsed < 60:
            st.button(f"Reenviar codigo ({int(60-elapsed)}s)", disabled=True,
                      use_container_width=True)
        else:
            if st.button("Reenviar codigo", use_container_width=True):
                try:
                    _enviar_codigo_2fa()
                    st.success("Nuevo codigo enviado a tu correo.")
                except Exception as e:
                    st.error(f"Error: {e}")
                st.rerun()

    if st.session_state["2fa_intentos"] > 0:
        st.warning(f"Intentos fallidos: {st.session_state['2fa_intentos']} / 5")


def _enviar_codigo_2fa():
    """Genera, envia y guarda el codigo 2FA."""
    codigo = email_service.generar_codigo_otp(6)
    codigo_hash = email_service.hashear_codigo(codigo)
    # Guardar en DB
    cfg = {}
    try:
        cfg = database.obtener_configuracion()
    except Exception:
        pass
    validez = int(cfg.get("2fa_validez_minutos", "10") or 10)
    database.guardar_codigo_2fa(
        st.session_state.visitante_id,
        st.session_state.visitante_correo,
        codigo_hash,
        validez_minutos=validez,
    )
    # Enviar correo
    email_service.enviar_codigo_2fa(
        st.session_state.visitante_correo, codigo,
        nombre=st.session_state.visitante_nombre,
    )
    # Guardar id del codigo mas reciente
    codigo_db = database.verificar_codigo_2fa(st.session_state.visitante_id)
    if codigo_db:
        st.session_state["2fa_codigo_id"] = codigo_db["id"]
    st.session_state["2fa_reenviado_en"] = time.time()


def _validar_2fa(codigo_ingresado: str):
    codigo_ingresado = (codigo_ingresado or "").strip()
    if not codigo_ingresado.isdigit() or len(codigo_ingresado) != 6:
        st.error("El codigo debe ser 6 digitos numericos.")
        return

    codigo_db = database.verificar_codigo_2fa(st.session_state.visitante_id)
    if not codigo_db:
        st.error("El codigo ha expirado. Solicita uno nuevo con 'Reenviar codigo'.")
        return

    if email_service.verificar_codigo(codigo_ingresado, codigo_db["codigo_hash"]):
        # Exito
        database.marcar_codigo_usado(codigo_db["id"])
        database.actualizar_visitante(st.session_state.visitante_id,
                                       {"email_validado": True})
        database.registrar_acceso("visitante", st.session_state.get("visitante_id", ""),
                                    "2fa_ok", correo=st.session_state.visitante_correo,
                                    exitoso=True)
        st.session_state.visitante_paso = 3
        st.session_state.crucigrama_inicio = time.time()
        st.success("Correo verificado correctamente.")
        time.sleep(0.8)
        st.rerun()
    else:
        # Fallo
        nuevos_intentos = database.incrementar_intento_2fa(codigo_db["id"])
        st.session_state["2fa_intentos"] = nuevos_intentos
        database.registrar_acceso("visitante", st.session_state.visitante_id,
                                   "2fa_fail", correo=st.session_state.visitante_correo,
                                   detalle=f"Intento {nuevos_intentos}", exitoso=False)
        if nuevos_intentos >= 5:
            st.error("Has superado el maximo de intentos. Contacta al administrador.")
            if st.button("Volver al inicio"):
                _reset_state()
                st.switch_page("app.py")
        else:
            st.error(f"Codigo incorrecto. Intentos restantes: {5 - nuevos_intentos}")


# ---------------------------------------------------------------------------
# PASO 3: Crucigrama
# ---------------------------------------------------------------------------
def paso_crucigrama():
    st.markdown('<h2 class="card-title">🧩 Paso 3: Crucigrama SST (20 palabras)</h2>',
                unsafe_allow_html=True)
    styles.render_stepper(["Registro", "Verificacion", "Crucigrama", "Listo"], 2)

    st.markdown("""
    <div class="alert-info">
        Resuelve el crucigrama digitando las letras en cada casilla. Puedes resolver
        en cualquier orden. Cuando completes las 20 palabras con el 100% de aciertos,
        quedas automaticamente inscrito en el sorteo del premio sorpresa.
    </div>
    """, unsafe_allow_html=True)

    # Layout
    grid = cw.obtener_grid()
    filas, cols = cw.obtener_dimensiones()
    pistas = cw.obtener_pistas_por_direccion()

    # Panel de pistas
    st.markdown('<h3 style="color:#0D47A1; margin-top:1rem;">📋 Pistas</h3>',
                unsafe_allow_html=True)
    pc1, pc2 = st.columns(2)
    with pc1:
        st.markdown("""
        <div class="card" style="padding:1rem;">
            <h4 style="color:#1565C0; margin:0 0 0.5rem 0;">➡️ Horizontales</h4>
        </div>
        """, unsafe_allow_html=True)
        for p in pistas["horizontales"]:
            st.markdown(f"""
            <div style="margin:0.5rem 0; padding:0.5rem 0.75rem; background:#F5F7FA;
                        border-radius:8px; font-size:0.88rem; color:#1A2332;">
                <strong style="color:#1565C0;">{p['numero']}.</strong> {p['pista']}
                <span style="color:#5F6B7A; font-size:0.8rem;"> ({len(p['palabra'])} letras)</span>
            </div>
            """, unsafe_allow_html=True)
    with pc2:
        st.markdown("""
        <div class="card" style="padding:1rem;">
            <h4 style="color:#2E7D32; margin:0 0 0.5rem 0;">⬇️ Verticales</h4>
        </div>
        """, unsafe_allow_html=True)
        for p in pistas["verticales"]:
            st.markdown(f"""
            <div style="margin:0.5rem 0; padding:0.5rem 0.75rem; background:#F5F7FA;
                        border-radius:8px; font-size:0.88rem; color:#1A2332;">
                <strong style="color:#2E7D32;">{p['numero']}.</strong> {p['pista']}
                <span style="color:#5F6B7A; font-size:0.8rem;"> ({len(p['palabra'])} letras)</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<h3 style="color:#0D47A1;">🎯 Tu Crucigrama</h3>', unsafe_allow_html=True)

    # Renderizar grid
    respuestas = st.session_state.crucigrama_respuestas
    html_grid = '<div class="crossword-wrapper"><div class="crossword-grid" style="grid-template-columns: repeat(' + str(cols) + ', auto);">'
    for i in range(filas):
        for j in range(cols):
            if grid[i][j] == "":
                html_grid += '<div class="cw-cell blocked"></div>'
            else:
                num = cw.obtener_numero_en_celda(i, j)
                num_html = f'<span class="num">{num}</span>' if num else ""
                key = f"{i},{j}"
                val = respuestas.get(key, "")
                cls = "cw-cell"
                estado = cw.validar_celda_individual(respuestas, i, j)
                if estado:
                    cls += f" {estado}"
                html_grid += f'<div class="{cls}">{num_html}<input type="text" maxlength="1" data-key="{key}" value="{val}" /></div>'
    html_grid += "</div></div>"
    st.markdown(html_grid, unsafe_allow_html=True)

    # Inputs ocultos via streamlit para capturar valores (ya que HTML puro no se captura)
    # Solucion: usar st.text_input en una matriz
    st.markdown("""
    <div class="alert-warning" style="margin-top:1rem;">
        <strong>📖 Instrucciones:</strong> Digita cada letra en el cuadro correspondiente.
        Usa las pistas de arriba para resolver las palabras horizontales (➡️) y verticales (⬇️).
        Cuando termines, presiona el boton "Verificar respuestas".
    </div>
    """, unsafe_allow_html=True)

    # Formulario de captura (invisible pero funcional)
    _render_inputs_crucigrama(grid, filas, cols, respuestas)

    # Boton verificar
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        if st.button("✅ Verificar respuestas", use_container_width=True, type="primary"):
            _verificar_crucigrama()
    with col2:
        if st.button("🧹 Limpiar"):
            st.session_state.crucigrama_respuestas = {}
            st.rerun()
    with col3:
        if st.button("🏠 Inicio"):
            _reset_state()
            st.switch_page("app.py")


def _render_inputs_crucigrama(grid, filas, cols, respuestas):
    """Renderiza inputs de texto para capturar las letras del visitante.
    El grid visual arriba es solo referencial; estos inputs son los reales."""
    st.markdown("""
    <div class="card" style="margin-top:1rem;">
        <h4 style="color:#0D47A1; margin:0 0 0.5rem 0;">✍️ Ingresa tus respuestas por palabra</h4>
        <p style="color:#5F6B7A; font-size:0.85rem; margin:0 0 1rem 0;">
            Cada cuadro corresponde a una palabra del crucigrama (numerada segun las pistas).
            Digita las letras en orden (sin espacios).
        </p>
    </div>
    """, unsafe_allow_html=True)

    palabras_orden = cw.palabras_ordenadas()
    # Mostrar en columnas para que sea mas compacto en movil
    n = len(palabras_orden)
    cols_per_row = 2
    for idx in range(0, n, cols_per_row):
        chunk = palabras_orden[idx:idx + cols_per_row]
        cks = st.columns(cols_per_row)
        for k, p in enumerate(chunk):
            with cks[k]:
                clave = f"cw_{p['numero']}_{p['direccion']}"
                # Inicializar con valor previo
                valor_actual = ""
                # Reconstruir valor desde respuestas almacenadas
                for i in range(len(p["palabra"])):
                    if p["direccion"] == "H":
                        key = f"{p['fila']},{p['col'] + i}"
                    else:
                        key = f"{p['fila'] + i},{p['col']}"
                    valor_actual += respuestas.get(key, "")
                flecha = "➡️" if p["direccion"] == "H" else "⬇️"
                label = f"{flecha} {p['numero']}. ({len(p['palabra'])} letras)"
                valor = st.text_input(label, value=valor_actual, max_chars=len(p["palabra"]),
                                       key=clave, placeholder="." * len(p["palabra"]))
                # Actualizar respuestas
                valor = (valor or "").upper()
                for i in range(len(p["palabra"])):
                    if p["direccion"] == "H":
                        key = f"{p['fila']},{p['col'] + i}"
                    else:
                        key = f"{p['fila'] + i},{p['col']}"
                    letra = valor[i] if i < len(valor) else ""
                    respuestas[key] = letra


def _verificar_crucigrama():
    respuestas = st.session_state.crucigrama_respuestas
    # Filtrar vacios
    respuestas_clean = {k: v for k, v in respuestas.items() if v}
    if len(respuestas_clean) == 0:
        st.warning("No has digitado ninguna respuesta. Completa el crucigrama e intenta de nuevo.")
        return

    resultado = cw.validar_respuestas(respuestas_clean)
    tiempo_total = int(time.time() - st.session_state.crucigrama_inicio) if st.session_state.crucigrama_inicio else None

    # Guardar intento
    try:
        database.guardar_intento_crucigrama(
            visitante_id=st.session_state.visitante_id,
            respuestas=respuestas_clean,
            aciertos=resultado["aciertos"],
            total=resultado["total"],
            completado=resultado["completado"],
            tiempo_segundos=tiempo_total,
        )
    except Exception as e:
        st.error(f"Error guardando intento: {e}")
        return

    database.registrar_acceso("visitante", st.session_state.visitante_id,
                               "crucigrama_verificado",
                               correo=st.session_state.visitante_correo,
                               detalle=f"aciertos: {resultado['aciertos']}/{resultado['total']}",
                               exitoso=True)

    if resultado["completado"]:
        st.balloons()
        st.success(f"¡Felicitaciones! Has completado el crucigrama al 100% "
                    f"({resultado['aciertos']}/{resultado['total']}).")
        st.session_state.visitante_paso = 4
        st.session_state.crucigrama_resultado = resultado
        time.sleep(1.5)
        st.rerun()
    else:
        st.warning(f"Vas bien, pero te faltan {resultado['total'] - resultado['aciertos']} "
                    f"palabras por corregir. Puntaje actual: {resultado['puntaje']}%.")
        # Mostrar detalle
        with st.expander("Ver detalle por palabra"):
            for pal in resultado["palabras_correctas"]:
                icono = "✅" if pal["ok"] else "❌"
                flecha = "➡️" if pal["direccion"] == "H" else "⬇️"
                st.markdown(f"**{icono} {flecha} {pal['numero']}.** Esperada: `{pal['palabra']}` "
                            f"&middot; Tu respuesta: `{pal['respuesta_visitante'] or '(vacia)'}`")


# ---------------------------------------------------------------------------
# PASO 4: Finalizado
# ---------------------------------------------------------------------------
def paso_finalizado():
    st.markdown('<h2 class="card-title">🎉 ¡Listo! Crucigrama Completado</h2>',
                unsafe_allow_html=True)
    styles.render_stepper(["Registro", "Verificacion", "Crucigrama", "Listo"], 3)
    resultado = st.session_state.get("crucigrama_resultado", {})
    puntaje = resultado.get("puntaje", 100)
    aciertos = resultado.get("aciertos", 20)
    total = resultado.get("total", 20)

    st.markdown(f"""
    <div class="alert-success">
        <strong>¡Felicitaciones {st.session_state.visitante_nombre}!</strong><br>
        Has completado el crucigrama con <strong>{aciertos}/{total}</strong> aciertos
        ({puntaje}% de efectividad). Quedas automaticamente inscrito en el sorteo
        del <strong>premio sorpresa</strong> que se realizara en la sesion de cierre
        del evento.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <h3 style="color:#1565C0; margin-top:0;">📊 Tu participacion</h3>
        <p>Tu nombre esta ahora en la lista oficial de participantes elegibles para el
        sorteo. La ruleta se ejecutara en vivo durante la sesion de cierre, frente a
        todos los asistentes, para garantizar transparencia.</p>
        <p>Recuerda asistir al cierre del evento para presenciar el sorteo.
        Si resultas ganador, recibirás una notificacion por correo al termino del sorteo.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🏠 Volver al inicio", use_container_width=True):
        _reset_state()
        st.switch_page("app.py")


def _reset_state():
    """Limpia el estado del visitante."""
    keys = ["visitante_paso", "visitante_id", "visitante_nombre", "visitante_correo",
            "2fa_codigo_id", "2fa_intentos", "2fa_reenviado_en",
            "crucigrama_respuestas", "crucigrama_inicio", "crucigrama_resultado"]
    for k in keys:
        if k in st.session_state:
            del st.session_state[k]


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
def main():
    paso = st.session_state.visitante_paso
    if paso == 1:
        paso_registro()
    elif paso == 2:
        paso_2fa()
    elif paso == 3:
        paso_crucigrama()
    elif paso == 4:
        paso_finalizado()
    styles.render_footer()


if __name__ == "__main__":
    main()
