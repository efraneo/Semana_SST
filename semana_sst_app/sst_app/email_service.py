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
    """Obtiene las credenciales SMTP desde st.secrets o variables de entorno."""
    try:
        import streamlit as st
        cfg = st.secrets.get("smtp", {})
    except Exception:
        cfg = {}
    return {
        "host": cfg.get("host") or os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "port": int(cfg.get("port") or os.getenv("SMTP_PORT", "465")),
        "user": cfg.get("user") or os.getenv("SMTP_USER"),
        "password": cfg.get("password") or os.getenv("SMTP_PASSWORD"),
        "from_name": cfg.get("from_name") or os.getenv("SMTP_FROM_NAME", "Semana SST - Clinica San Rafael"),
        "from_email": cfg.get("from_email") or os.getenv("SMTP_FROM_EMAIL") or cfg.get("user"),
    }


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
    cfg = _get_secrets()
    if not cfg["user"] or not cfg["password"]:
        raise RuntimeError(
            "Falta configurar SMTP. Define smtp.user y smtp.password en .streamlit/secrets.toml"
        )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Tu codigo de verificacion - Semana SST Clinica San Rafael"
    msg["From"] = f"{cfg['from_name']} <{cfg['from_email']}>"
    msg["To"] = correo_destino

    html = _construir_html(codigo, nombre)
    texto = (
        f"Hola {nombre},\n\n"
        f"Tu codigo de verificacion para la Semana SST es: {codigo}\n\n"
        f"Este codigo es valido por 10 minutos.\n\n"
        f"Clinica San Rafael Alta Complejidad SAS"
    )
    msg.attach(MIMEText(texto, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    context = ssl.create_default_context()
    try:
        if cfg["port"] == 465:
            with smtplib.SMTP_SSL(cfg["host"], cfg["port"], context=context, timeout=20) as srv:
                srv.login(cfg["user"], cfg["password"])
                srv.sendmail(cfg["from_email"], [correo_destino], msg.as_string())
        else:
            with smtplib.SMTP(cfg["host"], cfg["port"], timeout=20) as srv:
                srv.starttls(context=context)
                srv.login(cfg["user"], cfg["password"])
                srv.sendmail(cfg["from_email"], [correo_destino], msg.as_string())
        return True
    except Exception as e:
        raise RuntimeError(f"Error enviando correo: {e}") from e


def enviar_notificacion_ganador(correo_destino: str, nombre: str, premio: str) -> bool:
    """Envia notificacion al visitante ganador del premio."""
    cfg = _get_secrets()
    if not cfg["user"] or not cfg["password"]:
        return False
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "¡Felicitaciones! Eres el ganador del premio sorpresa - Semana SST"
    msg["From"] = f"{cfg['from_name']} <{cfg['from_email']}>"
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
    try:
        if cfg["port"] == 465:
            with smtplib.SMTP_SSL(cfg["host"], cfg["port"], context=context, timeout=20) as srv:
                srv.login(cfg["user"], cfg["password"])
                srv.sendmail(cfg["from_email"], [correo_destino], msg.as_string())
        else:
            with smtplib.SMTP(cfg["host"], cfg["port"], timeout=20) as srv:
                srv.starttls(context=context)
                srv.login(cfg["user"], cfg["password"])
                srv.sendmail(cfg["from_email"], [correo_destino], msg.as_string())
        return True
    except Exception:
        return False
