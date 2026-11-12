"""
Modulo de acceso a Supabase para la app Semana SST.
Encapsula todas las operaciones CRUD y consultas.
"""
from __future__ import annotations
import os
from datetime import datetime, timezone
from typing import Any, Optional

try:
    from supabase import create_client, Client
except ImportError:  # pragma: no cover
    Client = None
    create_client = None


# ---------------------------------------------------------------------------
# Configuracion
# ---------------------------------------------------------------------------

def _get_secrets():
    """Obtiene credenciales desde st.secrets o variables de entorno."""
    try:
        import streamlit as st
        sb = st.secrets.get("supabase", {})
        return {
            "url": sb.get("url") or os.getenv("SUPABASE_URL"),
            "key": sb.get("service_key") or os.getenv("SUPABASE_SERVICE_KEY"),
        }
    except Exception:
        return {
            "url": os.getenv("SUPABASE_URL"),
            "key": os.getenv("SUPABASE_SERVICE_KEY"),
        }


_cliente: Optional["Client"] = None


def get_client():
    """Retorna cliente Supabase (singleton)."""
    global _cliente
    if _cliente is not None:
        return _cliente
    if create_client is None:
        raise RuntimeError("Instala supabase-py: pip install supabase")
    sec = _get_secrets()
    if not sec["url"] or not sec["key"]:
        raise RuntimeError(
            "Falta configuracion de Supabase. Define SUPABASE_URL y SUPABASE_SERVICE_KEY "
            "en .streamlit/secrets.toml"
        )
    _cliente = create_client(sec["url"], sec["key"])
    return _cliente


# ---------------------------------------------------------------------------
# Tabla: visitantes
# ---------------------------------------------------------------------------

def crear_visitante(datos: dict) -> dict:
    """Inserta un nuevo visitante. Retorna el registro creado."""
    sb = get_client()
    # Limpieza
    payload = {
        "cedula": str(datos["cedula"]).strip(),
        "nombre": str(datos["nombre"]).strip().upper(),
        "cargo": str(datos["cargo"]).strip(),
        "correo": str(datos["correo"]).strip().lower(),
        "telefono": str(datos.get("telefono", "")).strip() or None,
        "empresa": str(datos["empresa"]).strip(),
        "habeas_data": bool(datos.get("habeas_data", False)),
        "habeas_data_fecha": datetime.now(timezone.utc).isoformat() if datos.get("habeas_data") else None,
    }
    resp = sb.table("visitantes").insert(payload).execute()
    return resp.data[0] if resp.data else {}


def buscar_visitante_por_cedula(cedula: str) -> Optional[dict]:
    sb = get_client()
    r = sb.table("visitantes").select("*").eq("cedula", str(cedula).strip()).execute()
    return r.data[0] if r.data else None


def buscar_visitante_por_correo(correo: str) -> Optional[dict]:
    sb = get_client()
    r = sb.table("visitantes").select("*").eq("correo", correo.strip().lower()).execute()
    return r.data[0] if r.data else None


def obtener_visitante(visitante_id: str) -> Optional[dict]:
    sb = get_client()
    r = sb.table("visitantes").select("*").eq("id", visitante_id).execute()
    return r.data[0] if r.data else None


def actualizar_visitante(visitante_id: str, cambios: dict) -> dict:
    sb = get_client()
    # Filtrar nulos vacios para no sobrescribir
    clean = {k: v for k, v in cambios.items() if v is not None or k == "telefono"}
    r = sb.table("visitantes").update(clean).eq("id", visitante_id).execute()
    return r.data[0] if r.data else {}


def listar_visitantes(limit: int = 1000, offset: int = 0) -> list[dict]:
    sb = get_client()
    r = (sb.table("visitantes")
         .select("*")
         .order("creado_en", desc=True)
         .range(offset, offset + limit - 1)
         .execute())
    return r.data or []


def eliminar_visitante(visitante_id: str) -> bool:
    sb = get_client()
    sb.table("visitantes").delete().eq("id", visitante_id).execute()
    return True


# ---------------------------------------------------------------------------
# Tabla: codigos_2fa
# ---------------------------------------------------------------------------

def guardar_codigo_2fa(visitante_id: str, correo: str, codigo_hash: str,
                       validez_minutos: int = 10) -> dict:
    sb = get_client()
    from datetime import timedelta
    expira = (datetime.now(timezone.utc) + timedelta(minutes=validez_minutos)).isoformat()
    payload = {
        "visitante_id": visitante_id,
        "correo_destino": correo,
        "codigo_hash": codigo_hash,
        "expires_at": expira,
    }
    r = sb.table("codigos_2fa").insert(payload).execute()
    return r.data[0] if r.data else {}


def verificar_codigo_2fa(visitante_id: str) -> Optional[dict]:
    """Obtiene el codigo 2FA mas reciente y vigente para el visitante."""
    sb = get_client()
    r = (sb.table("codigos_2fa")
         .select("*")
         .eq("visitante_id", visitante_id)
         .eq("usado", False)
         .order("creado_en", desc=True)
         .limit(1)
         .execute())
    if not r.data:
        return None
    codigo = r.data[0]
    # Verificar expiracion
    expira_str = codigo["expires_at"].replace("Z", "+00:00")
    expira = datetime.fromisoformat(expira_str)
    if datetime.now(timezone.utc) > expira:
        return None
    return codigo


def marcar_codigo_usado(codigo_id: str):
    sb = get_client()
    sb.table("codigos_2fa").update({"usado": True}).eq("id", codigo_id).execute()


def incrementar_intento_2fa(codigo_id: str) -> int:
    sb = get_client()
    r = sb.table("codigos_2fa").select("intentos").eq("id", codigo_id).execute()
    if not r.data:
        return 0
    nuevo = (r.data[0].get("intentos") or 0) + 1
    sb.table("codigos_2fa").update({"intentos": nuevo}).eq("id", codigo_id).execute()
    return nuevo


# ---------------------------------------------------------------------------
# Tabla: intentos_crucigrama
# ---------------------------------------------------------------------------

def guardar_intento_crucigrama(visitante_id: str, respuestas: dict,
                                aciertos: int, total: int, completado: bool,
                                tiempo_segundos: Optional[int] = None) -> dict:
    sb = get_client()
    puntaje = int(round((aciertos / total) * 100)) if total else 0
    payload = {
        "visitante_id": visitante_id,
        "respuestas": respuestas,
        "aciertos": aciertos,
        "total_palabras": total,
        "puntaje": puntaje,
        "completado": completado,
        "tiempo_segundos": tiempo_segundos,
    }
    r = sb.table("intentos_crucigrama").insert(payload).execute()
    # Actualizar el estado del visitante
    if completado:
        actualizar_visitante(visitante_id, {
            "crucigrama_completado": True,
            "crucigrama_puntaje": puntaje,
            "crucigrama_resuelto_en": datetime.now(timezone.utc).isoformat(),
        })
    else:
        # Guardar mejor puntaje alcanzado
        v = obtener_visitante(visitante_id)
        if v and puntaje > (v.get("crucigrama_puntaje") or 0):
            actualizar_visitante(visitante_id, {"crucigrama_puntaje": puntaje})
    return r.data[0] if r.data else {}


def listar_intentos_visitante(visitante_id: str) -> list[dict]:
    sb = get_client()
    r = (sb.table("intentos_crucigrama")
         .select("*")
         .eq("visitante_id", visitante_id)
         .order("creado_en", desc=True)
         .execute())
    return r.data or []


# ---------------------------------------------------------------------------
# Tabla: accesos_log
# ---------------------------------------------------------------------------

def registrar_acceso(tipo_usuario: str, usuario_ref: str, accion: str,
                     correo: str = "", detalle: str = "",
                     ip: str = "", user_agent: str = "",
                     exitoso: bool = True):
    """Registra un acceso en la bitacora. No levanta excepciones si falla."""
    try:
        sb = get_client()
        sb.table("accesos_log").insert({
            "tipo_usuario": tipo_usuario,
            "usuario_ref": usuario_ref,
            "correo": correo,
            "accion": accion,
            "detalle": detalle,
            "ip_origen": ip,
            "user_agent": user_agent,
            "exitoso": exitoso,
        }).execute()
    except Exception as e:
        # La bitacora no debe romper el flujo principal
        print(f"[WARN] No se pudo registrar acceso: {e}")


def listar_accesos(limit: int = 200) -> list[dict]:
    sb = get_client()
    r = (sb.table("accesos_log")
         .select("*")
         .order("creado_en", desc=True)
         .limit(limit)
         .execute())
    return r.data or []


# ---------------------------------------------------------------------------
# Tabla: administradores
# ---------------------------------------------------------------------------

def buscar_admin_por_usuario(usuario: str) -> Optional[dict]:
    sb = get_client()
    r = sb.table("administradores").select("*").eq("usuario", usuario.strip()).eq("activo", True).execute()
    return r.data[0] if r.data else None


def crear_admin(usuario: str, password_hash: str, nombre: str, correo: str,
                rol: str = "admin") -> dict:
    sb = get_client()
    r = sb.table("administradores").insert({
        "usuario": usuario,
        "password_hash": password_hash,
        "nombre_completo": nombre,
        "correo": correo,
        "rol": rol,
    }).execute()
    return r.data[0] if r.data else {}


def listar_admins() -> list[dict]:
    sb = get_client()
    r = sb.table("administradores").select("*").order("creado_en", desc=True).execute()
    return r.data or []


# ---------------------------------------------------------------------------
# Tabla: premios y sorteos_ruleta
# ---------------------------------------------------------------------------

def listar_premios() -> list[dict]:
    sb = get_client()
    r = sb.table("premios").select("*").order("creado_en", desc=True).execute()
    return r.data or []


def actualizar_premio(premio_id: str, cambios: dict):
    sb = get_client()
    sb.table("premios").update(cambios).eq("id", premio_id).execute()


def listar_participantes_ruleta() -> list[dict]:
    """Visitantes elegibles para el sorteo (crucigrama completado)."""
    sb = get_client()
    r = sb.table("visitantes").select("id, cedula, nombre, cargo, correo, empresa, "
                                      "crucigrama_puntaje, crucigrama_resuelto_en, creado_en") \
        .eq("crucigrama_completado", True) \
        .eq("email_validado", True) \
        .eq("habeas_data", True) \
        .order("crucigrama_resuelto_en") \
        .execute()
    return r.data or []


def guardar_sorteo(premio_id: str, admin_id: str, participantes_total: int,
                   ganador_id: str, semilla: str) -> dict:
    sb = get_client()
    payload = {
        "premio_id": premio_id,
        "admin_id": admin_id,
        "participantes_total": participantes_total,
        "ganador_id": ganador_id,
        "semilla": semilla,
    }
    r = sb.table("sorteos_ruleta").insert(payload).execute()
    # Marcar premio como sorteado
    if r.data:
        actualizar_premio(premio_id, {
            "estado": "sorteado",
            "ganador_id": ganador_id,
            "fecha_sorteo": datetime.now(timezone.utc).isoformat(),
        })
    return r.data[0] if r.data else {}


def listar_sorteos() -> list[dict]:
    sb = get_client()
    r = sb.table("sorteos_ruleta").select("*").order("ejecutado_en", desc=True).execute()
    return r.data or []


# ---------------------------------------------------------------------------
# Tabla: cronograma
# ---------------------------------------------------------------------------

def listar_cronograma() -> list[dict]:
    sb = get_client()
    r = sb.table("cronograma").select("*").order("dia, hora_inicio").execute()
    return r.data or []


def crear_cronograma(datos: dict) -> dict:
    sb = get_client()
    r = sb.table("cronograma").insert(datos).execute()
    return r.data[0] if r.data else {}


def actualizar_cronograma(item_id: str, cambios: dict):
    sb = get_client()
    sb.table("cronograma").update(cambios).eq("id", item_id).execute()


def eliminar_cronograma(item_id: str):
    sb = get_client()
    sb.table("cronograma").delete().eq("id", item_id).execute()


# ---------------------------------------------------------------------------
# Tabla: configuracion
# ---------------------------------------------------------------------------

def obtener_configuracion() -> dict:
    sb = get_client()
    r = sb.table("configuracion").select("*").execute()
    return {row["clave"]: row["valor"] for row in (r.data or [])}


def actualizar_configuracion(clave: str, valor: str):
    sb = get_client()
    sb.table("configuracion").update({"valor": valor}).eq("clave", clave).execute()


# ---------------------------------------------------------------------------
# Vista: estadisticas
# ---------------------------------------------------------------------------

def obtener_estadisticas() -> dict:
    sb = get_client()
    r = sb.table("visitantes").select("email_validado, crucigrama_completado, habeas_data, empresa").execute()
    data = r.data or []
    total = len(data)
    return {
        "total_registrados": total,
        "total_validados": sum(1 for v in data if v.get("email_validado")),
        "total_crucigrama_ok": sum(1 for v in data if v.get("crucigrama_completado")),
        "total_habeas_data": sum(1 for v in data if v.get("habeas_data")),
        "total_empresas": len(set(v.get("empresa") for v in data if v.get("empresa"))),
    }
