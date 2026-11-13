"""
Autenticacion de administradores (login con usuario/contrasena + bcrypt).
Maneja sesion en st.session_state.
"""
from __future__ import annotations
import streamlit as st

import database


def is_logged_in() -> bool:
    return st.session_state.get("admin_user") is not None


def get_current_admin() -> dict | None:
    return st.session_state.get("admin_user")


def login(usuario: str, password: str) -> tuple[bool, str]:
    """Verifica credenciales. Retorna (ok, mensaje)."""
    usuario = (usuario or "").strip()
    if not usuario or not password:
        return False, "Ingresa usuario y contrasena."
    try:
        import bcrypt
    except ImportError:
        return False, "Falta instalar bcrypt (pip install bcrypt)."
    admin = database.buscar_admin_por_usuario(usuario)
    if not admin:
        database.registrar_acceso("admin", usuario, "login_admin",
                                  detalle="Usuario inexistente", exitoso=False)
        return False, "Usuario o contrasena incorrectos."
    try:
        ok = bcrypt.checkpw(password.encode(), admin["password_hash"].encode())
    except Exception:
        ok = False
    if not ok:
        database.registrar_acceso("admin", usuario, "login_admin",
                                  correo=admin.get("correo", ""),
                                  detalle="Password incorrecto", exitoso=False)
        return False, "Usuario o contrasena incorrectos."
    if not admin.get("activo", True):
        return False, "El usuario administrador esta inactivo."
    st.session_state["admin_user"] = admin
    database.registrar_acceso("admin", usuario, "login_admin",
                              correo=admin.get("correo", ""), exitoso=True)
    return True, "Acceso correcto."


def logout():
    admin = st.session_state.get("admin_user")
    if admin:
        database.registrar_acceso("admin", admin["usuario"], "logout_admin",
                                  correo=admin.get("correo", ""), exitoso=True)
    st.session_state.pop("admin_user", None)


def cambiar_password(usuario: str, password_actual: str, password_nuevo: str) -> tuple[bool, str]:
    """Permite al admin cambiar su propia contrasena."""
    import bcrypt
    admin = database.buscar_admin_por_usuario(usuario)
    if not admin:
        return False, "Usuario no encontrado."
    if not bcrypt.checkpw(password_actual.encode(), admin["password_hash"].encode()):
        return False, "La contrasena actual no es correcta."
    if len(password_nuevo) < 8:
        return False, "La nueva contrasena debe tener al menos 8 caracteres."
    nuevo_hash = bcrypt.hashpw(password_nuevo.encode(), bcrypt.gensalt(12)).decode()
    database.actualizar_visitante  # noqa (evitar import sin uso)
    database.get_client().table("sst_administradores").update(
        {"password_hash": nuevo_hash}
    ).eq("id", admin["id"]).execute()
    return True, "Contrasena actualizada con exito."


def require_login():
    """Verifica sesion. Si no hay, renderiza login y detiene ejecucion."""
    if is_logged_in():
        return
    st.warning("Debes iniciar sesion para acceder a esta seccion.")
    st.stop()
