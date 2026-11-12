"""
SCRIPT DE CONFIGURACION INICIAL - SEMANA SST
=============================================
Crea el usuario administrador con un hash bcrypt valido.

USO:
    1. Configura .streamlit/secrets.toml con tus credenciales de Supabase
    2. Ejecuta el esquema SQL (supabase_schema.sql) en el SQL Editor de Supabase
    3. Ejecuta este script:
        python crear_admin.py
    4. Ingresa usuario, contrasena y correo cuando se te pida
    5. Inicia la app:
        streamlit run app.py
"""
import sys
import os
import getpass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bcrypt
from src import database


def crear_admin_interactivo():
    print("=" * 60)
    print("  Creacion de administrador - Semana SST")
    print("  Clinica San Rafael Alta Complejidad SAS")
    print("=" * 60)

    usuario = input("Usuario (ej. admin): ").strip()
    if not usuario:
        print("Usuario obligatorio. Abortando.")
        return

    correo = input("Correo: ").strip()
    if "@" not in correo:
        print("Correo invalido. Abortando.")
        return

    nombre = input("Nombre completo: ").strip()
    if not nombre:
        print("Nombre obligatorio. Abortando.")
        return

    password = getpass.getpass("Contrasena (min 8 caracteres): ")
    if len(password) < 8:
        print("La contrasena debe tener al menos 8 caracteres. Abortando.")
        return

    password2 = getpass.getpass("Confirmar contrasena: ")
    if password != password2:
        print("Las contrasenas no coinciden. Abortando.")
        return

    rol = input("Rol (admin / super_admin) [admin]: ").strip() or "admin"

    # Verificar si ya existe
    existente = database.buscar_admin_por_usuario(usuario)
    if existente:
        print(f"Ya existe un admin con usuario '{usuario}'.")
        confirmar = input("Deseas actualizar la contrasena? (s/n): ").lower()
        if confirmar != "s":
            print("Operacion cancelada.")
            return
        nuevo_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()
        database.get_client().table("administradores").update(
            {"password_hash": nuevo_hash, "nombre_completo": nombre,
             "correo": correo, "rol": rol}
        ).eq("id", existente["id"]).execute()
        print(f"Admin '{usuario}' actualizado correctamente.")
        return

    # Crear nuevo
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()
    try:
        nuevo = database.crear_admin(usuario, password_hash, nombre, correo, rol)
        print("\n" + "=" * 60)
        print(f"  Admin creado correctamente.")
        print(f"  ID: {nuevo.get('id')}")
        print(f"  Usuario: {usuario}")
        print(f"  Nombre: {nombre}")
        print(f"  Correo: {correo}")
        print(f"  Rol: {rol}")
        print("=" * 60)
        print("\nAhora puedes iniciar sesion en la app:")
        print("  streamlit run app.py")
    except Exception as e:
        print(f"Error: {e}")
        print("\nVerifica que:")
        print("  1. Hayas ejecutado el esquema SQL en Supabase")
        print("  2. Las credenciales en .streamlit/secrets.toml sean correctas")
        print("  3. La tabla 'administradores' exista")


if __name__ == "__main__":
    try:
        crear_admin_interactivo()
    except KeyboardInterrupt:
        print("\nOperacion cancelada por el usuario.")
    except Exception as e:
        print(f"\nError inesperado: {e}")
        sys.exit(1)
