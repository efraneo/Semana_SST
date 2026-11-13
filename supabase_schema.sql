-- ============================================================================
-- SEMANA SST - CLINICA SAN RAFAEL ALTA COMPLEJIDAD SAS
-- Esquema de base de datos para Supabase (PostgreSQL)
-- Todas las tablas usan prefijo "sst_" para evitar conflictos con tablas
-- existentes en tu proyecto de Supabase.
-- ============================================================================

-- ============================================================================
-- 0. LIMPIEZA SEGURA (idempotente, no falla si algo no existe)
-- Solo DROP TABLE ... CASCADE (elimina triggers y policies automaticamente)
-- ============================================================================
DROP VIEW IF EXISTS sst_v_participantes_ruleta CASCADE;
DROP VIEW IF EXISTS sst_v_estadisticas_evento CASCADE;
DROP VIEW IF EXISTS v_participantes_ruleta CASCADE;
DROP VIEW IF EXISTS v_estadisticas_evento CASCADE;

DROP TABLE IF EXISTS sst_sorteos_ruleta CASCADE;
DROP TABLE IF EXISTS sst_premios CASCADE;
DROP TABLE IF EXISTS sst_intentos_crucigrama CASCADE;
DROP TABLE IF EXISTS sst_codigos_2fa CASCADE;
DROP TABLE IF EXISTS sst_accesos_log CASCADE;
DROP TABLE IF EXISTS sst_cronograma CASCADE;
DROP TABLE IF EXISTS sst_configuracion CASCADE;
DROP TABLE IF EXISTS sst_visitantes CASCADE;
DROP TABLE IF EXISTS sst_administradores CASCADE;

-- Tambien eliminamos las versiones sin prefijo por si quedaron de una
-- ejecucion anterior incompleta (NO toca tus otras tablas existentes)
DROP TABLE IF EXISTS sorteos_ruleta CASCADE;
DROP TABLE IF EXISTS premios CASCADE;
DROP TABLE IF EXISTS intentos_crucigrama CASCADE;
DROP TABLE IF EXISTS codigos_2fa CASCADE;
DROP TABLE IF EXISTS accesos_log CASCADE;
DROP TABLE IF EXISTS cronograma CASCADE;
DROP TABLE IF EXISTS configuracion CASCADE;
DROP TABLE IF EXISTS visitantes CASCADE;
DROP TABLE IF EXISTS administradores CASCADE;

DROP FUNCTION IF EXISTS sst_actualizar_timestamp() CASCADE;
DROP FUNCTION IF EXISTS actualizar_timestamp() CASCADE;

-- ============================================================================
-- 1. TABLA: sst_administradores
-- ============================================================================
CREATE TABLE sst_administradores (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario         TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    nombre_completo TEXT NOT NULL,
    correo          TEXT NOT NULL UNIQUE,
    rol             TEXT NOT NULL DEFAULT 'admin',
    activo          BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE sst_administradores IS 'Usuarios con acceso al panel administrativo de Semana SST';

-- ============================================================================
-- 2. TABLA: sst_visitantes
-- ============================================================================
CREATE TABLE sst_visitantes (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cedula                TEXT NOT NULL UNIQUE,
    nombre                TEXT NOT NULL,
    cargo                 TEXT NOT NULL,
    correo                TEXT NOT NULL,
    telefono              TEXT,
    empresa               TEXT NOT NULL,
    habeas_data           BOOLEAN NOT NULL DEFAULT FALSE,
    habeas_data_fecha     TIMESTAMPTZ,
    email_validado        BOOLEAN NOT NULL DEFAULT FALSE,
    crucigrama_completado BOOLEAN NOT NULL DEFAULT FALSE,
    crucigrama_puntaje    INTEGER NOT NULL DEFAULT 0,
    crucigrama_resuelto_en TIMESTAMPTZ,
    ip_registro           TEXT,
    user_agent            TEXT,
    creado_en             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE sst_visitantes IS 'Visitantes registrados a la Semana SST';

CREATE INDEX idx_sst_visitantes_correo ON sst_visitantes (correo);
CREATE INDEX idx_sst_visitantes_cedula ON sst_visitantes (cedula);
CREATE INDEX idx_sst_visitantes_email_validado ON sst_visitantes (email_validado);
CREATE INDEX idx_sst_visitantes_crucigrama ON sst_visitantes (crucigrama_completado);
CREATE INDEX idx_sst_visitantes_creado ON sst_visitantes (creado_en DESC);

-- ============================================================================
-- 3. TABLA: sst_codigos_2fa
-- ============================================================================
CREATE TABLE sst_codigos_2fa (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    visitante_id    UUID REFERENCES sst_visitantes(id) ON DELETE CASCADE,
    correo_destino  TEXT NOT NULL,
    codigo_hash     TEXT NOT NULL,
    expires_at      TIMESTAMPTZ NOT NULL,
    usado           BOOLEAN NOT NULL DEFAULT FALSE,
    intentos        INTEGER NOT NULL DEFAULT 0,
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sst_codigos_2fa_visitante ON sst_codigos_2fa (visitante_id);
CREATE INDEX idx_sst_codigos_2fa_correo ON sst_codigos_2fa (correo_destino);
CREATE INDEX idx_sst_codigos_2fa_expires ON sst_codigos_2fa (expires_at);

-- ============================================================================
-- 4. TABLA: sst_intentos_crucigrama
-- ============================================================================
CREATE TABLE sst_intentos_crucigrama (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    visitante_id    UUID REFERENCES sst_visitantes(id) ON DELETE CASCADE,
    respuestas      JSONB NOT NULL,
    aciertos        INTEGER NOT NULL DEFAULT 0,
    total_palabras  INTEGER NOT NULL DEFAULT 20,
    puntaje         INTEGER NOT NULL DEFAULT 0,
    completado      BOOLEAN NOT NULL DEFAULT FALSE,
    tiempo_segundos INTEGER,
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sst_intentos_visitante ON sst_intentos_crucigrama (visitante_id);
CREATE INDEX idx_sst_intentos_completado ON sst_intentos_crucigrama (completado);

-- ============================================================================
-- 5. TABLA: sst_accesos_log
-- ============================================================================
CREATE TABLE sst_accesos_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tipo_usuario    TEXT NOT NULL,
    usuario_ref     TEXT,
    correo          TEXT,
    accion          TEXT NOT NULL,
    detalle         TEXT,
    ip_origen       TEXT,
    user_agent      TEXT,
    exitoso         BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sst_accesos_log_tipo ON sst_accesos_log (tipo_usuario);
CREATE INDEX idx_sst_accesos_log_usuario ON sst_accesos_log (usuario_ref);
CREATE INDEX idx_sst_accesos_log_creado ON sst_accesos_log (creado_en DESC);

-- ============================================================================
-- 6. TABLA: sst_premios
-- ============================================================================
CREATE TABLE sst_premios (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre          TEXT NOT NULL,
    descripcion     TEXT,
    fecha_sorteo    TIMESTAMPTZ,
    ganador_id      UUID REFERENCES sst_visitantes(id) ON DELETE SET NULL,
    estado          TEXT NOT NULL DEFAULT 'pendiente',
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE sst_premios IS 'Premios y ganadores del sorteo final';

-- ============================================================================
-- 7. TABLA: sst_sorteos_ruleta
-- ============================================================================
CREATE TABLE sst_sorteos_ruleta (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    premio_id           UUID REFERENCES sst_premios(id) ON DELETE CASCADE,
    admin_id            UUID REFERENCES sst_administradores(id) ON DELETE SET NULL,
    participantes_total INTEGER NOT NULL DEFAULT 0,
    ganador_id          UUID REFERENCES sst_visitantes(id) ON DELETE SET NULL,
    semilla             TEXT NOT NULL,
    ejecutado_en        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sst_sorteos_ganador ON sst_sorteos_ruleta (ganador_id);

-- ============================================================================
-- 8. TABLA: sst_cronograma
-- ============================================================================
CREATE TABLE sst_cronograma (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dia             DATE NOT NULL,
    hora_inicio     TIME NOT NULL,
    hora_fin        TIME NOT NULL,
    actividad       TEXT NOT NULL,
    descripcion     TEXT,
    responsable     TEXT,
    ubicacion       TEXT,
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actualizado_en  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sst_cronograma_dia ON sst_cronograma (dia, hora_inicio);

-- ============================================================================
-- 9. TABLA: sst_configuracion
-- ============================================================================
CREATE TABLE sst_configuracion (
    clave           TEXT PRIMARY KEY,
    valor           TEXT NOT NULL,
    descripcion     TEXT,
    actualizado_en  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO sst_configuracion (clave, valor, descripcion) VALUES
    ('evento_nombre', 'Semana SST 2025', 'Nombre del evento mostrado en la app'),
    ('evento_fecha_inicio', '2025-11-17', 'Fecha de inicio (YYYY-MM-DD)'),
    ('evento_fecha_fin', '2025-11-21', 'Fecha de fin (YYYY-MM-DD)'),
    ('premio_descripcion', 'Premio sorpresa entregado en la sesion de cierre', 'Descripcion del premio'),
    ('crucigrama_intentos_maximos', '3', 'Numero maximo de intentos del crucigrama'),
    ('2fa_validez_minutos', '10', 'Validez en minutos del codigo 2FA')
ON CONFLICT (clave) DO NOTHING;

-- ============================================================================
-- 10. FUNCION Y TRIGGERS: actualizar actualizado_en automaticamente
-- ============================================================================
CREATE OR REPLACE FUNCTION sst_actualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.actualizado_en = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_sst_visitantes_ts BEFORE UPDATE ON sst_visitantes
FOR EACH ROW EXECUTE FUNCTION sst_actualizar_timestamp();

CREATE TRIGGER trg_sst_admin_ts BEFORE UPDATE ON sst_administradores
FOR EACH ROW EXECUTE FUNCTION sst_actualizar_timestamp();

CREATE TRIGGER trg_sst_premios_ts BEFORE UPDATE ON sst_premios
FOR EACH ROW EXECUTE FUNCTION sst_actualizar_timestamp();

CREATE TRIGGER trg_sst_cronograma_ts BEFORE UPDATE ON sst_cronograma
FOR EACH ROW EXECUTE FUNCTION sst_actualizar_timestamp();

CREATE TRIGGER trg_sst_config_ts BEFORE UPDATE ON sst_configuracion
FOR EACH ROW EXECUTE FUNCTION sst_actualizar_timestamp();

-- ============================================================================
-- 11. ROW LEVEL SECURITY (RLS)
-- ============================================================================
ALTER TABLE sst_visitantes ENABLE ROW LEVEL SECURITY;
ALTER TABLE sst_administradores ENABLE ROW LEVEL SECURITY;
ALTER TABLE sst_codigos_2fa ENABLE ROW LEVEL SECURITY;
ALTER TABLE sst_intentos_crucigrama ENABLE ROW LEVEL SECURITY;
ALTER TABLE sst_accesos_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE sst_premios ENABLE ROW LEVEL SECURITY;
ALTER TABLE sst_sorteos_ruleta ENABLE ROW LEVEL SECURITY;
ALTER TABLE sst_cronograma ENABLE ROW LEVEL SECURITY;
ALTER TABLE sst_configuracion ENABLE ROW LEVEL SECURITY;

-- Politicas: service_role puede todo
CREATE POLICY sst_role_all_visitantes ON sst_visitantes
    FOR ALL TO service_role USING (TRUE) WITH CHECK (TRUE);
CREATE POLICY sst_role_all_admin ON sst_administradores
    FOR ALL TO service_role USING (TRUE) WITH CHECK (TRUE);
CREATE POLICY sst_role_all_2fa ON sst_codigos_2fa
    FOR ALL TO service_role USING (TRUE) WITH CHECK (TRUE);
CREATE POLICY sst_role_all_intentos ON sst_intentos_crucigrama
    FOR ALL TO service_role USING (TRUE) WITH CHECK (TRUE);
CREATE POLICY sst_role_all_log ON sst_accesos_log
    FOR ALL TO service_role USING (TRUE) WITH CHECK (TRUE);
CREATE POLICY sst_role_all_premios ON sst_premios
    FOR ALL TO service_role USING (TRUE) WITH CHECK (TRUE);
CREATE POLICY sst_role_all_sorteos ON sst_sorteos_ruleta
    FOR ALL TO service_role USING (TRUE) WITH CHECK (TRUE);

-- anon solo puede leer cronograma y configuracion
CREATE POLICY sst_anon_read_cronograma ON sst_cronograma
    FOR SELECT TO anon, service_role USING (TRUE);
CREATE POLICY sst_role_all_cronograma ON sst_cronograma
    FOR ALL TO service_role USING (TRUE) WITH CHECK (TRUE);

CREATE POLICY sst_anon_read_config ON sst_configuracion
    FOR SELECT TO anon, service_role USING (TRUE);
CREATE POLICY sst_role_all_config ON sst_configuracion
    FOR ALL TO service_role USING (TRUE) WITH CHECK (TRUE);

-- ============================================================================
-- 12. VISTA: sst_v_participantes_ruleta
-- ============================================================================
CREATE OR REPLACE VIEW sst_v_participantes_ruleta AS
SELECT
    id, cedula, nombre, cargo, correo, empresa,
    crucigrama_puntaje, crucigrama_resuelto_en,
    creado_en
FROM sst_visitantes
WHERE crucigrama_completado = TRUE
  AND email_validado = TRUE
  AND habeas_data = TRUE
ORDER BY crucigrama_resuelto_en;

COMMENT ON VIEW sst_v_participantes_ruleta IS 'Visitantes elegibles para el sorteo del premio';

-- ============================================================================
-- 13. VISTA: sst_v_estadisticas_evento
-- ============================================================================
CREATE OR REPLACE VIEW sst_v_estadisticas_evento AS
SELECT
    COUNT(*) AS total_registrados,
    COUNT(*) FILTER (WHERE email_validado) AS total_validados,
    COUNT(*) FILTER (WHERE crucigrama_completado) AS total_crucigrama_ok,
    COUNT(*) FILTER (WHERE habeas_data) AS total_habeas_data,
    COUNT(DISTINCT empresa) AS total_empresas
FROM sst_visitantes;

-- ============================================================================
-- 14. ADMIN POR DEFECTO
-- Usuario: admin / Contrasena: AdminSST2025! (CAMBIAR al primer ingreso)
-- ============================================================================
INSERT INTO sst_administradores (usuario, password_hash, nombre_completo, correo, rol)
VALUES (
    'admin',
    '$2b$12$t.0Riyi1BjLvjo/49u5hZeMACAXefoDCOm62/zF7J3C44nEUOcghq',
    'Administrador Semana SST',
    'admin@clinicasanrafael.com',
    'super_admin'
)
ON CONFLICT (usuario) DO NOTHING;

-- ============================================================================
-- 15. DATOS DE EJEMPLO: CRONOGRAMA
-- ============================================================================
INSERT INTO sst_cronograma (dia, hora_inicio, hora_fin, actividad, descripcion, responsable, ubicacion) VALUES
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
INSERT INTO sst_premios (nombre, descripcion, estado)
VALUES ('Premio sorpresa Semana SST 2025', 'Premio sorpresa entregado al visitante ganador de la ruleta durante la sesion de cierre', 'pendiente')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- VERIFICACION FINAL
-- ============================================================================
SELECT 'Esquema SST creado correctamente' AS mensaje;
SELECT tablename AS tablas_sst_creadas 
FROM pg_tables 
WHERE schemaname = 'public' AND tablename LIKE 'sst_%'
ORDER BY tablename;
