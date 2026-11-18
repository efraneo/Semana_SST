"""
Servicio de correo para 2FA via Gmail SMTP.
Genera codigo OTP, lo envia y lo hashea para verificacion.
"""
from __future__ import annotations
import os
import secrets
import smtplib
import ssl
import bcrypt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional


def _get_secrets() -> dict:
    """Obtiene las credenciales SMTP desde st.secrets o variables de entorno.
    Soporta varios formatos:
      - Plano: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_NOMBRE_REMITENTE
      - Seccion [smtp]: host, port, user, password, from_name, from_email
      - Varias variantes de claves
    Siempre devuelve strings (vacios si faltan), nunca None."""
    user = None
    password = None
    from_name = None
    from_email = None
    try:
        import streamlit as st
        if "smtp" in st.secrets:
            cfg = st.secrets["smtp"]
        else:
            cfg = {}
        user = cfg.get("user") or cfg.get("SMTP_USER")
        password = cfg.get("password") or cfg.get("SMTP_PASSWORD")
        from_name = (cfg.get("from_name") or cfg.get("SMTP_FROM_NAME")
                     or cfg.get("SMTP_NOMBRE_REMITENTE") or cfg.get("nombre_remitente"))
        from_email = cfg.get("from_email") or cfg.get("SMTP_FROM_EMAIL")
        # Tambien soportar claves planas en st.secrets (formato SMTP_*)
        if not user:
            user = st.secrets.get("SMTP_USER") or st.secrets.get("smtp_user")
        if not password:
            password = st.secrets.get("SMTP_PASSWORD") or st.secrets.get("smtp_password")
        if not from_name:
            from_name = (st.secrets.get("SMTP_NOMBRE_REMITENTE")
                         or st.secrets.get("SMTP_FROM_NAME")
                         or st.secrets.get("smtp_from_name"))
        if not from_email:
            from_email = st.secrets.get("SMTP_FROM_EMAIL") or st.secrets.get("smtp_from_email")
    except Exception:
        pass
    # Fallback a variables de entorno
    if not user:
        user = os.getenv("SMTP_USER") or os.getenv("smtp_user")
    if not password:
        password = os.getenv("SMTP_PASSWORD") or os.getenv("smtp_password")
    if not from_name:
        from_name = (os.getenv("SMTP_NOMBRE_REMITENTE")
                     or os.getenv("SMTP_FROM_NAME")
                     or "Semana SST - Clinica San Rafael")
    if not from_email:
        from_email = os.getenv("SMTP_FROM_EMAIL") or user  # Si no hay from_email, usar user

    return {
        "host": _safe_get("host", "smtp.gmail.com"),
        "port": _safe_int("port", 587),
        "user": user or "",
        "password": password or "",
        "from_name": from_name or "Semana SST - Clinica San Rafael",
        "from_email": from_email or "",
    }


def _safe_get(key, default):
    """Obtiene un valor string de st.secrets (seccion smtp o plano) o variables de entorno."""
    val = None
    try:
        import streamlit as st
        if "smtp" in st.secrets:
            val = st.secrets["smtp"].get(key)
        if not val:
            val = st.secrets.get(key.upper())
            # Variante en espanol
            if not val and key == "from_name":
                val = st.secrets.get("SMTP_NOMBRE_REMITENTE")
    except Exception:
        pass
    if not val:
        env_key = f"SMTP_{key.upper()}"
        val = os.getenv(env_key) or os.getenv(key)
        # Variante en espanol
        if not val and key == "from_name":
            val = os.getenv("SMTP_NOMBRE_REMITENTE")
    return val or default


def _safe_int(key, default):
    val = _safe_get(key, None)
    if val is None:
        return default
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


def generar_codigo_otp(longitud: int = 6) -> str:
    """Genera un codigo OTP numerico de 6 digitos."""
    return "".join(str(secrets.randbelow(10)) for _ in range(longitud))


def hashear_codigo(codigo: str) -> str:
    """Hashea el codigo con bcrypt para almacenarlo de forma segura."""
    return bcrypt.hashpw(codigo.encode(), bcrypt.gensalt(12)).decode()


def verificar_codigo(codigo_ingresado: str, codigo_hash: str) -> bool:
    """Verifica el codigo ingresado contra el hash almacenado."""
    try:
        return bcrypt.checkpw(codigo_ingresado.encode(), codigo_hash.encode())
    except Exception:
        return False


def _construir_html(codigo: str, nombre_visitante: str = "") -> str:
    """Construye el cuerpo HTML del correo 2FA."""
    saludo = f"Hola <strong>{nombre_visitante}</strong>," if nombre_visitante else "Hola,"
    return f"""
<!DOCTYPE html>
<html lang="es">
<head><meta charset="utf-8"></head>
<body style="font-family: 'Segoe UI', Arial, sans-serif; background:#F5F7FA; margin:0; padding:0;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#F5F7FA; padding:32px 0;">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0" style="background:#FFFFFF; border-radius:16px; overflow:hidden; box-shadow:0 4px 16px rgba(21,101,192,0.10);">
        <tr>
          <td style="background:linear-gradient(135deg, #1565C0 0%, #0D47A1 100%); padding:28px 32px;">
            <h1 style="color:#FFFFFF; margin:0; font-size:20px; font-weight:700;">Clinica San Rafael</h1>
            <p style="color:#E3F2FD; margin:4px 0 0 0; font-size:13px;">Alta Complejidad SAS - Semana SST</p>
          </td>
        </tr>
        <tr>
          <td style="padding:32px;">
            <p style="color:#1A2332; font-size:15px; line-height:1.6;">{saludo}</p>
            <p style="color:#1A2332; font-size:15px; line-height:1.6;">
              Has iniciado el registro para participar en la Semana SST.
              Para continuar, ingresa el siguiente codigo de verificacion en la aplicacion:
            </p>
            <div style="background:rgba(21,101,192,0.08); border:2px dashed #1565C0; border-radius:12px;
                        padding:24px; text-align:center; margin:24px 0;">
              <span style="font-size:38px; font-weight:700; color:#1565C0; letter-spacing:8px; font-family:'Courier New', monospace;">
                {codigo}
              </span>
            </div>
            <p style="color:#5F6B7A; font-size:13px; line-height:1.5;">
              Este codigo es valido por <strong>10 minutos</strong> y de uso unico.
              Si no solicitaste este codigo, ignora este mensaje.
            </p>
            <hr style="border:none; border-top:1px solid #E1E5EB; margin:24px 0;">
            <p style="color:#5F6B7A; font-size:12px; line-height:1.5;">
              Mensaje automatico - no responder a este correo.<br>
              Clinica San Rafael Alta Complejidad SAS - Sistema de Gestion SST
            </p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>
"""


def enviar_codigo_2fa(correo_destino: str, codigo: str, nombre: str = "") -> bool:
    """Envia el codigo 2FA al correo del visitante via Gmail SMTP. Retorna True si OK."""
    # Validaciones de entrada
    if not correo_destino or not isinstance(correo_destino, str) or not correo_destino.strip():
        raise RuntimeError("Correo destino vacio o invalido para envio 2FA.")
    if not codigo or not isinstance(codigo, str):
        raise RuntimeError("Codigo 2FA vacio o invalido.")
    correo_destino = correo_destino.strip()
    nombre = (nombre or "").strip()

    cfg = _get_secrets()
    if not cfg["user"] or not cfg["password"]:
        raise RuntimeError(
            "Falta configurar SMTP. Define smtp.user y smtp.password en .streamlit/secrets.toml "
            "o en Streamlit Cloud -> Settings -> Secrets."
        )
    # Asegurar from_email
    from_email = cfg["from_email"] or cfg["user"]
    from_name = cfg["from_name"] or "Semana SST - Clinica San Rafael"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Tu codigo de verificacion - Semana SST Clinica San Rafael"
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = correo_destino

    html = _construir_html(codigo, nombre)
    texto = (
        f"Hola {nombre or 'visitante'},\n\n"
        f"Tu codigo de verificacion para la Semana SST es: {codigo}\n\n"
        f"Este codigo es valido por 10 minutos.\n\n"
        f"Clinica San Rafael Alta Complejidad SAS"
    )
    msg.attach(MIMEText(texto, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    context = ssl.create_default_context()
    try:
        if cfg["port"] == 465:
            # Puerto 465: SMTP sobre SSL directo
            with smtplib.SMTP_SSL(cfg["host"], cfg["port"], context=context, timeout=30) as srv:
                srv.login(cfg["user"], cfg["password"])
                srv.sendmail(from_email, [correo_destino], msg.as_string())
        else:
            # Puerto 587 (o 25): SMTP con STARTTLS
            with smtplib.SMTP(cfg["host"], cfg["port"], timeout=30) as srv:
                # Activar depuracion para mejor diagnostico en caso de error
                srv.ehlo()
                srv.starttls(context=context)
                srv.ehlo()
                srv.login(cfg["user"], cfg["password"])
                srv.sendmail(from_email, [correo_destino], msg.as_string())
        return True
    except smtplib.SMTPAuthenticationError as e:
        # Error tipico: app password incorrecta o 2FA no activado en Gmail
        raise RuntimeError(
            f"Error de autenticacion SMTP ({e.smtp_code}): {e.smtp_error.decode() if isinstance(e.smtp_error, bytes) else e.smtp_error}. "
            f"Verifica que: (1) tengas activada la verificacion en 2 pasos en Gmail, "
            f"(2) estes usando una 'App Password' de 16 caracteres (no tu clave normal). "
            f"Generala en https://myaccount.google.com/apppasswords"
        ) from e
    except smtplib.SMTPException as e:
        raise RuntimeError(f"Error SMTP ({getattr(e, 'smtp_code', '?')}): {e}") from e
    except Exception as e:
        raise RuntimeError(f"Error enviando correo: {type(e).__name__}: {e}") from e


def enviar_notificacion_ganador(correo_destino: str, nombre: str, premio: str) -> bool:
    """Envia notificacion al visitante ganador del premio. No levanta excepciones."""
    try:
        if not correo_destino or not isinstance(correo_destino, str) or not correo_destino.strip():
            return False
        correo_destino = correo_destino.strip()
        nombre = (nombre or "").strip()
        cfg = _get_secrets()
        if not cfg["user"] or not cfg["password"]:
            return False
        from_email = cfg["from_email"] or cfg["user"]
        from_name = cfg["from_name"] or "Semana SST - Clinica San Rafael"
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "¡Felicitaciones! Eres el ganador del premio sorpresa - Semana SST"
        msg["From"] = f"{from_name} <{from_email}>"
        msg["To"] = correo_destino
        html = f"""
<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"></head>
<body style="font-family:'Segoe UI',Arial,sans-serif; background:#FFF8E1; margin:0; padding:32px 0;">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0" style="background:#FFFFFF; border-radius:16px; overflow:hidden; box-shadow:0 4px 16px rgba(237,108,2,0.20);">
        <tr>
          <td style="background:linear-gradient(135deg,#ED6C02 0%,#BF360C 100%); padding:28px 32px;">
            <h1 style="color:#FFFFFF; margin:0; font-size:22px;">¡Felicitaciones, {nombre}!</h1>
            <p style="color:#FFF3E0; margin:4px 0 0 0; font-size:13px;">Has ganado el premio sorpresa de la Semana SST</p>
          </td>
        </tr>
        <tr><td style="padding:32px;">
          <p style="color:#1A2332; font-size:15px;">
            Estimado/a <strong>{nombre}</strong>, hemos realizado el sorteo aleatorio de la ruleta
            frente a todos los participantes y tu nombre ha sido seleccionado como ganador del
            <strong>{premio}</strong>.
          </p>
          <p style="color:#1A2332; font-size:15px;">
            El premio sera entregado en la sesion de cierre del evento. Presenta este correo
            o tu cedula para reclamarlo.
          </p>
          <p style="color:#5F6B7A; font-size:13px;">
            Clinica San Rafael Alta Complejidad SAS - Semana SST
          </p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body></html>
"""
        texto = (f"¡Felicitaciones {nombre}! Has ganado el {premio} en la Semana SST. "
                  "El premio sera entregado en la sesion de cierre.")
        msg.attach(MIMEText(texto, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))
        context = ssl.create_default_context()
        if cfg["port"] == 465:
            with smtplib.SMTP_SSL(cfg["host"], cfg["port"], context=context, timeout=30) as srv:
                srv.login(cfg["user"], cfg["password"])
                srv.sendmail(from_email, [correo_destino], msg.as_string())
        else:
            with smtplib.SMTP(cfg["host"], cfg["port"], timeout=30) as srv:
                srv.ehlo()
                srv.starttls(context=context)
                srv.ehlo()
                srv.login(cfg["user"], cfg["password"])
                srv.sendmail(from_email, [correo_destino], msg.as_string())
        return True
    except Exception as e:
        print(f"[WARN] No se pudo enviar notificacion al ganador: {e}")
        return False
