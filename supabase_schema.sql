-- ============================================================================
-- SEMANA SST - CLINICA SAN RAFAEL ALTA COMPLEJIDAD SAS
-- Esquema de base de datos para Supabase (PostgreSQL)
-- Ejecutar: copiar y pegar en SQL Editor de Supabase
-- ============================================================================

-- ============================================================================
-- 1. TABLA: administradores
-- Usuarios administradores con acceso al panel CRUD/ruleta
-- ============================================================================
CREATE TABLE IF NOT EXISTS administradores (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario         TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,                  -- hash bcrypt (ej. $2b$12$...)
    nombre_completo TEXT NOT NULL,
    correo          TEXT NOT NULL UNIQUE,
    rol             TEXT NOT NULL DEFAULT 'admin',   -- admin | super_admin
    activo          BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE administradores IS 'Usuarios con acceso al panel administrativo de Semana SST';

-- ============================================================================
-- 2. TABLA: visitantes
-- Datos personales del visitante + consentimiento habeas data
-- ============================================================================
CREATE TABLE IF NOT EXISTS visitantes (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cedula              TEXT NOT NULL UNIQUE,
    nombre              TEXT NOT NULL,
    cargo               TEXT NOT NULL,
    correo              TEXT NOT NULL,
    telefono            TEXT,
    empresa             TEXT NOT NULL,
    habeas_data         BOOLEAN NOT NULL DEFAULT FALSE,   -- true = acepto
    habeas_data_fecha   TIMESTAMPTZ,                       -- momento del consentimiento
    email_validado      BOOLEAN NOT NULL DEFAULT FALSE,    -- true = completo 2FA
    crucigrama_completado BOOLEAN NOT NULL DEFAULT FALSE,
    crucigrama_puntaje  INTEGER NOT NULL DEFAULT 0,        -- % de aciertos (0-100)
    crucigrama_resuelto_en TIMESTAMPTZ,                    -- momento de finalizacion
    ip_registro         TEXT,
    user_agent          TEXT,
    creado_en           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE visitantes IS 'Visitantes registrados a la Semana SST';

CREATE INDEX IF NOT EXISTS idx_visitantes_correo ON visitantes (correo);
CREATE INDEX IF NOT EXISTS idx_visitantes_cedula ON visitantes (cedula);
CREATE INDEX IF NOT EXISTS idx_visitantes_email_validado ON visitantes (email_validado);
CREATE INDEX IF NOT EXISTS idx_visitantes_crucigrama_completado ON visitantes (crucigrama_completado);
CREATE INDEX IF NOT EXISTS idx_visitantes_creado_en ON visitantes (creado_en DESC);

-- ============================================================================
-- 3. TABLA: codigos_2fa
-- Códigos OTP de un solo uso enviados por correo para validar identidad
-- ============================================================================
CREATE TABLE IF NOT EXISTS codigos_2fa (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    visitante_id    UUID REFERENCES visitantes(id) ON DELETE CASCADE,
    correo_destino  TEXT NOT NULL,
    codigo_hash     TEXT NOT NULL,                  -- hash bcrypt del codigo
    expires_at      TIMESTAMPTZ NOT NULL,           -- validez 10 min
    usado           BOOLEAN NOT NULL DEFAULT FALSE,
    intentos       INTEGER NOT NULL DEFAULT 0,     -- max 5 intentos
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_codigos_2fa_visitante ON codigos_2fa (visitante_id);
CREATE INDEX IF NOT EXISTS idx_codigos_2fa_correo ON codigos_2fa (correo_destino);
CREATE INDEX IF NOT EXISTS idx_codigos_2fa_expires ON codigos_2fa (expires_at);

-- ============================================================================
-- 4. TABLA: intentos_crucigrama
-- Historial de intentos del crucigrama por cada visitante
-- ============================================================================
CREATE TABLE IF NOT EXISTS intentos_crucigrama (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    visitante_id    UUID REFERENCES visitantes(id) ON DELETE CASCADE,
    respuestas      JSONB NOT NULL,                 -- {"0,0": "B", "0,1": "I", ...}
    aciertos        INTEGER NOT NULL DEFAULT 0,
    total_palabras  INTEGER NOT NULL DEFAULT 20,
    puntaje         INTEGER NOT NULL DEFAULT 0,     -- 0-100
    completado      BOOLEAN NOT NULL DEFAULT FALSE,
    tiempo_segundos INTEGER,                        -- duracion del intento
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_intentos_visitante ON intentos_crucigrama (visitante_id);
CREATE INDEX IF NOT EXISTS idx_intentos_completado ON intentos_crucigrama (completado);

-- ============================================================================
-- 5. TABLA: accesos_log
-- Bitácora de ingresos (visitantes y admin) para auditoria
-- ============================================================================
CREATE TABLE IF NOT EXISTS accesos_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tipo_usuario    TEXT NOT NULL,                  -- 'visitante' | 'admin'
    usuario_ref     TEXT,                           -- cedula o username
    correo          TEXT,
    accion          TEXT NOT NULL,                  -- 'registro' | 'login_admin' | '2fa_ok' | '2fa_fail' | 'crucigrama_completado' | ...
    detalle         TEXT,
    ip_origen       TEXT,
    user_agent      TEXT,
    exitoso         BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_accesos_log_tipo ON accesos_log (tipo_usuario);
CREATE INDEX IF NOT EXISTS idx_accesos_log_usuario ON accesos_log (usuario_ref);
CREATE INDEX IF NOT EXISTS idx_accesos_log_creado ON accesos_log (creado_en DESC);

-- ============================================================================
-- 6. TABLA: premios
-- Registro del premio sorpresa del cierre del evento
-- ============================================================================
CREATE TABLE IF NOT EXISTS premios (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre          TEXT NOT NULL,                 -- 'Premio sorpresa Semana SST 2025'
    descripcion     TEXT,
    fecha_sorteo    TIMESTAMPTZ,
    ganador_id      UUID REFERENCES visitantes(id) ON DELETE SET NULL,
    estado          TEXT NOT NULL DEFAULT 'pendiente', -- 'pendiente' | 'sorteado' | 'entregado'
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE premios IS 'Premios y ganadores del sorteo final';

-- ============================================================================
-- 7. TABLA: sorteos_ruleta
-- Historial de ejecuciones de la ruleta (transparencia)
-- ============================================================================
CREATE TABLE IF NOT EXISTS sorteos_ruleta (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    premio_id           UUID REFERENCES premios(id) ON DELETE CASCADE,
    admin_id            UUID REFERENCES administradores(id) ON DELETE SET NULL,
    participantes_total INTEGER NOT NULL DEFAULT 0,
    ganador_id          UUID REFERENCES visitantes(id) ON DELETE SET NULL,
    semilla             TEXT NOT NULL,              -- semilla usada para reproducibilidad
    ejecutado_en        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sorteos_ganador ON sorteos_ruleta (ganador_id);

-- ============================================================================
-- 8. TABLA: cronograma
-- Agenda de la Semana SST (visible para admin y visitantes)
-- ============================================================================
CREATE TABLE IF NOT EXISTS cronograma (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dia             DATE NOT NULL,                  -- fecha de la actividad
    hora_inicio     TIME NOT NULL,
    hora_fin        TIME NOT NULL,
    actividad       TEXT NOT NULL,
    descripcion     TEXT,
    responsable     TEXT,
    ubicacion       TEXT,
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cronograma_dia ON cronograma (dia, hora_inicio);

-- ============================================================================
-- 9. TABLA: configuracion
-- Parametros generales de la app (editable desde admin)
-- ============================================================================
CREATE TABLE IF NOT EXISTS configuracion (
    clave           TEXT PRIMARY KEY,
    valor           TEXT NOT NULL,
    descripcion     TEXT,
    actualizado_en  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO configuracion (clave, valor, descripcion) VALUES
    ('evento_nombre', 'Semana SST 2025', 'Nombre del evento mostrado en la app'),
    ('evento_fecha_inicio', '2025-11-17', 'Fecha de inicio (YYYY-MM-DD)'),
    ('evento_fecha_fin', '2025-11-21', 'Fecha de fin (YYYY-MM-DD)'),
    ('premio_descripcion', 'Premio sorpresa entregado en la sesion de cierre', 'Descripcion del premio'),
    ('crucigrama_intentos_maximos', '3', 'Numero maximo de intentos del crucigrama'),
    ('2fa_validez_minutos', '10', 'Validez en minutos del codigo 2FA')
ON CONFLICT (clave) DO NOTHING;

-- ============================================================================
-- 10. TRIGGERS: actualizar actualizado_en automaticamente
-- ============================================================================
CREATE OR REPLACE FUNCTION actualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_visitantes_ts ON visitantes;
CREATE TRIGGER trg_visitantes_ts BEFORE UPDATE ON visitantes
FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

DROP TRIGGER IF EXISTS trg_admin_ts ON administradores;
CREATE TRIGGER trg_admin_ts BEFORE UPDATE ON administradores
FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

DROP TRIGGER IF EXISTS trg_premios_ts ON premios;
CREATE TRIGGER trg_premios_ts BEFORE UPDATE ON premios
FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

DROP TRIGGER IF EXISTS trg_cronograma_ts ON cronograma;
CREATE TRIGGER trg_cronograma_ts BEFORE UPDATE ON cronograma
FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

DROP TRIGGER IF EXISTS trg_config_ts ON configuracion;
CREATE TRIGGER trg_config_ts BEFORE UPDATE ON configuracion
FOR EACH ROW EXECUTE FUNCTION actualizar_timestamp();

-- ============================================================================
-- 11. ROW LEVEL SECURITY (RLS)
-- ============================================================================
ALTER TABLE visitantes ENABLE ROW LEVEL SECURITY;
ALTER TABLE administradores ENABLE ROW LEVEL SECURITY;
ALTER TABLE codigos_2fa ENABLE ROW LEVEL SECURITY;
ALTER TABLE intentos_crucigrama ENABLE ROW LEVEL SECURITY;
ALTER TABLE accesos_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE premios ENABLE ROW LEVEL SECURITY;
ALTER TABLE sorteos_ruleta ENABLE ROW LEVEL SECURITY;
ALTER TABLE cronograma ENABLE ROW LEVEL SECURITY;
ALTER TABLE configuracion ENABLE ROW LEVEL SECURITY;

-- Politica: el service_role (usado por la app con la SERVICE_KEY) puede todo.
-- anon solo puede consultar cronograma y configuracion (publicos).
CREATE POLICY "service_role_all_visitantes" ON visitantes
    FOR ALL TO service_role USING (TRUE) WITH CHECK (TRUE);

CREATE POLICY "service_role_all_admin" ON administradores
    FOR ALL TO service_role USING (TRUE) WITH CHECK (TRUE);

CREATE POLICY "service_role_all_2fa" ON codigos_2fa
    FOR ALL TO service_role USING (TRUE) WITH CHECK (TRUE);

CREATE POLICY "service_role_all_intentos" ON intentos_crucigrama
    FOR ALL TO service_role USING (TRUE) WITH CHECK (TRUE);

CREATE POLICY "service_role_all_log" ON accesos_log
    FOR ALL TO service_role USING (TRUE) WITH CHECK (TRUE);

CREATE POLICY "service_role_all_premios" ON premios
    FOR ALL TO service_role USING (TRUE) WITH CHECK (TRUE);

CREATE POLICY "service_role_all_sorteos" ON sorteos_ruleta
    FOR ALL TO service_role USING (TRUE) WITH CHECK (TRUE);

CREATE POLICY "anon_read_cronograma" ON cronograma
    FOR SELECT TO anon, service_role USING (TRUE);
CREATE POLICY "service_role_all_cronograma" ON cronograma
    FOR ALL TO service_role USING (TRUE) WITH CHECK (TRUE);

CREATE POLICY "anon_read_config" ON configuracion
    FOR SELECT TO anon, service_role USING (TRUE);
CREATE POLICY "service_role_all_config" ON configuracion
    FOR ALL TO service_role USING (TRUE) WITH CHECK (TRUE);

-- ============================================================================
-- 12. VISTA: v_participantes_ruleta
-- Visitantes elegibles para el sorteo (crucigrama 100% completado)
-- ============================================================================
CREATE OR REPLACE VIEW v_participantes_ruleta AS
SELECT
    id, cedula, nombre, cargo, correo, empresa,
    crucigrama_puntaje, crucigrama_resuelto_en,
    creado_en
FROM visitantes
WHERE crucigrama_completado = TRUE
  AND email_validado = TRUE
  AND habeas_data = TRUE
ORDER BY crucigrama_resuelto_en;

COMMENT ON VIEW v_participantes_ruleta IS 'Visitantes elegibles para el sorteo del premio';

-- ============================================================================
-- 13. VISTA: v_estadisticas_evento
-- Dashboard resumido para el admin
-- ============================================================================
CREATE OR REPLACE VIEW v_estadisticas_evento AS
SELECT
    COUNT(*) AS total_registrados,
    COUNT(*) FILTER (WHERE email_validado) AS total_validados,
    COUNT(*) FILTER (WHERE crucigrama_completado) AS total_crucigrama_ok,
    COUNT(*) FILTER (WHERE habeas_data) AS total_habeas_data,
    COUNT(DISTINCT empresa) AS total_empresas
FROM visitantes;

-- ============================================================================
-- 14. ADMIN POR DEFECTO
-- Usuario: admin
-- Contrasena temporal: AdminSST2025!  (CAMBIAR INMEDIATAMENTE desde la app)
-- Hash bcrypt ya generado, listo para insertar.
-- ============================================================================
INSERT INTO administradores (usuario, password_hash, nombre_completo, correo, rol)
VALUES (
    'admin',
    '$2b$12$t.0Riyi1BjLvjo/49u5hZeMACAXefoDCOm62/zF7J3C44nEUOcghq',
    'Administrador Semana SST',
    'admin@clinicasanrafael.com',
    'super_admin'
)
ON CONFLICT (usuario) DO NOTHING;

-- Verificacion (opcional, solo consulta):
-- SELECT usuario, nombre_completo, correo, rol, creado_en FROM administradores;

-- Para generar tu propio hash bcrypt ejecuta:
--   python -c "import bcrypt; print(bcrypt.hashpw(b'TU_PASSWORD', bcrypt.gensalt(12)).decode())"
-- Y actualiza el registro:
--   UPDATE administradores SET password_hash='NUEVO_HASH' WHERE usuario='admin';

-- ============================================================================
-- 15. DATOS DE EJEMPLO: CRONOGRAMA (editable desde el panel admin)
-- ============================================================================
INSERT INTO cronograma (dia, hora_inicio, hora_fin, actividad, descripcion, responsable, ubicacion) VALUES
    ('2025-11-17', '08:00', '09:00', 'Inauguracion Semana SST', 'Apertura oficial del evento y presentacion del cronograma', 'Comite SST', 'Auditorio principal'),
    ('2025-11-17', '09:00', '11:00', 'Capacitacion: SG-SST Resolucion 0312', 'Recorrido por los estandares minimos del SG-SST', 'Coordinador SST', 'Auditorio principal'),
    ('2025-11-18', '10:00', '12:00', 'Taller de bioseguridad clinica', 'Manejo de residuos hospitalarios y prevencion de pinchazos', 'Enfermeria EPS', 'Sala de capacitacion'),
    ('2025-11-19', '14:00', '16:00', 'Simulacro de evacuacion', 'Practica de evacuacion y uso de extintores', 'Brigada de emergencias', 'Todas las sedes'),
    ('2025-11-20', '09:00', '11:00', 'Ergonomia en el puesto de trabajo', 'Prevencion de lesiones musculo-esqueleticas', 'Fisioterapeuta', 'Sala multiusos'),
    ('2025-11-21', '15:00', '17:00', 'Cierre y sorteo del premio', 'Entrega de reconocimientos y sorteo entre participantes', 'Direccion', 'Auditorio principal')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 16. PREMIO POR DEFECTO
-- ============================================================================
INSERT INTO premios (nombre, descripcion, estado)
VALUES ('Premio sorpresa Semana SST 2025', 'Premio sorpresa entregado al visitante ganador de la ruleta durante la sesion de cierre', 'pendiente')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- FIN DEL ESQUEMA
-- ============================================================================
-- Verificacion rapida:
SELECT 'Tablas creadas' AS mensaje;
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;
