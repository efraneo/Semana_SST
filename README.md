# Semana SST - Clinica San Rafael Alta Complejidad SAS

App interactiva para la Semana de Salud y Seguridad en el Trabajo (SST).
Permite registrar visitantes con validacion 2FA por correo, resolver un
crucigrama de 20 palabras SST y realizar el sorteo del premio sorpresa
mediante una ruleta transparente en vivo.

## Caracteristicas

- **Registro de visitante** con cedula, nombre, cargo, correo, telefono y empresa
- **Consentimiento Habeas Data** (Ley 1581 de 2012)
- **Verificacion 2FA** por correo (Gmail SMTP) - codigo de 6 digitos, 10 min de validez
- **Crucigrama SST de 20 palabras** (mixto: clinico + normativa + riesgos generales)
- **Panel de administrador** con login usuario/contrasena
- **CRUD completo** de visitantes
- **Historial de accesos** (bitacora de auditoria)
- **Cronograma del evento** editable
- **Ruleta del premio** con seleccion aleatoria reproducible (semilla)
- **Notificacion automatica** al ganador por correo
- Almacenamiento en **Supabase** (PostgreSQL)
- Despliegue en **Streamlit Cloud**

## Estructura del proyecto

```
semana_sst_app/
├── app.py                          # Entry point - landing page
├── crear_admin.py                  # Script para crear admin inicial
├── requirements.txt
├── supabase_schema.sql             # Esquema SQL para Supabase (tablas con prefijo sst_)
├── README.md
├── .streamlit/
│   ├── config.toml                 # Tema visual
│   └── secrets.toml.example        # Plantilla de credenciales (copiar a secrets.toml)
├── assets/
│   └── logo.png                    # Logo (reemplazar con el real)
├── pages/
│   ├── 1_Visitante.py             # Flujo del visitante (registro + 2FA + crucigrama)
│   └── 2_Administrador.py          # Panel admin (CRUD + ruleta + historial)
└── sst_app/                         # Paquete de modulos (NO usar "src", conflicta en Streamlit Cloud)
    ├── __init__.py
    ├── styles.py                   # CSS y tema visual (azul clinica)
    ├── database.py                 # Acceso a Supabase (CRUD)
    ├── email_service.py            # Gmail SMTP 2FA
    ├── auth.py                     # Autenticacion admin (bcrypt)
    ├── crucigrama_data.py          # Carga del layout del crucigrama
    └── crucigrama_layout.json      # Layout generado (20 palabras)
```

> **Importante:** La carpeta de modulos se llama `sst_app/` (no `src/`) porque en Streamlit
> Cloud el repositorio se monta en `/mount/src/<repo>/`, y el nombre `src` genera conflicto
> con un namespace package implicito del sistema de archivos.

## Configuracion paso a paso

### 1. Crear proyecto en Supabase

1. Ve a https://app.supabase.com y crea un proyecto nuevo
2. Anota la **URL** del proyecto y la **service_role key** (no la anon)
3. En el SQL Editor, pega y ejecuta el contenido de `supabase_schema.sql`

### 2. Configurar Gmail SMTP (2FA)

1. Activa verificacion en 2 pasos en tu cuenta Gmail
2. Genera una "App password" en https://myaccount.google.com/apppasswords
3. Anota la contrasena de 16 caracteres

### 3. Configurar secrets

Copia `.streamlit/secrets.toml.example` como `.streamlit/secrets.toml` y completa:

```toml
[supabase]
url = "https://TU-PROYECTO.supabase.co"
service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6..."

[smtp]
host = "smtp.gmail.com"
port = 465
user = "tu_correo@gmail.com"
password = "abcd-efgh-ijkl-mnop"
from_name = "Semana SST - Clinica San Rafael"
from_email = "tu_correo@gmail.com"
```

### 4. Instalar dependencias y crear admin

```bash
pip install -r requirements.txt
python crear_admin.py
```

### 5. Ejecutar la app localmente

```bash
streamlit run app.py
```

### 6. Desplegar en Streamlit Cloud

1. Sube el proyecto a un repositorio GitHub (privado recomendado)
2. Ve a https://share.streamlit.io y conecta tu cuenta GitHub
3. Crea una nueva app:
   - Repository: tu_usuario/semana-sst-app
   - Branch: main
   - Main file path: app.py
4. En **Settings -> Secrets**, pega el contenido de `.streamlit/secrets.toml`
5. Click en **Deploy**

## Palabras del crucigrama (20)

Enfoque mixto balanceado:

| #  | Palabra        | Direccion | Enfoque        |
|----|----------------|-----------|----------------|
| 1  | BIOSEGURIDAD   | H         | Clinico        |
| 2  | CAPACITACION   | V         | General        |
| 3  | PREVENCION     | H         | General        |
| 4  | EVACUACION     | H         | General        |
| 5  | PROTECCION     | V         | General        |
| 6  | SEGURIDAD      | V         | General        |
| 7  | ERGONOMIA      | H         | General        |
| 8  | ACCIDENTE      | V         | Normativa      |
| 9  | RESIDUOS       | V         | Clinico        |
| 10 | PINCHAZO       | H         | Clinico        |
| 11 | EXTINTOR       | H         | General        |
| 12 | HIGIENE        | H         | Clinico        |
| 13 | ALTURAS        | H         | General        |
| 14 | BRIGADA        | V         | General        |
| 15 | RIESGO         | H         | Normativa      |
| 16 | LAVADO         | H         | Clinico        |
| 17 | SALUD          | V         | Normativa      |
| 18 | SGSST          | V         | Normativa      |
| 19 | MANOS          | V         | Clinico        |
| 20 | EPP            | V         | General        |

## Cumplimiento normativo

- Ley 1581 de 2012 (Habeas Data)
- Ley 1562 de 2012 (SST)
- Resolucion 0312 de 2019 (Estandares minimos SG-SST)
- Decreto 1072 de 2015 (Reglamentario SST)
- Decreto 1446 de 2012

## Seguridad

- Contrasenas hasheadas con bcrypt (cost factor 12)
- Codigos 2FA hasheados con bcrypt (no se almacenan en claro)
- RLS habilitado en todas las tablas
- Service role key solo se usa desde el backend (Streamlit Cloud secrets)
- Bitacora de accesos para auditoria
- Semilla de sorteo registrada para reproducibilidad

## Licencia

Uso interno - Clinica San Rafael Alta Complejidad SAS - diseñado por el Ing. Efrain Sarmiento Crespo
