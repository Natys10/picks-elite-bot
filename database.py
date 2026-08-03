import sqlite3
import logging
from config import DB_PATH, DEFAULT_START_TEXT

logger = logging.getLogger(__name__)

# =============================================
#   MOTOR DE BASE DE DATOS Y CONFIGURACIÓN DINÁMICA
# =============================================

class Database:
    def __init__(self):
        self.db_path = DB_PATH
        self.init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self._get_conn() as conn:
            # Tabla de usuarios
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    telegram_user_id     INTEGER PRIMARY KEY,
                    username             TEXT,
                    first_name           TEXT,
                    fecha_registro       TEXT DEFAULT CURRENT_TIMESTAMP,
                    fecha_click_gratis   TEXT,
                    estado               TEXT DEFAULT 'nuevo',
                    enviado_24h          INTEGER DEFAULT 0,
                    enviado_72h          INTEGER DEFAULT 0,
                    enviado_7d           INTEGER DEFAULT 0
                )
            """)
            # Tabla de configuracion dinamica (permite cambiar mensajes sin codigo)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS configuracion (
                    clave TEXT PRIMARY KEY,
                    valor TEXT
                )
            """)
            # Tabla de difusiones / campañas
            conn.execute("""
                CREATE TABLE IF NOT EXISTS campanas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT,
                    mensaje TEXT,
                    fecha_envio TEXT DEFAULT CURRENT_TIMESTAMP,
                    enviados INTEGER DEFAULT 0
                )
            """)
            # Tabla de logs de eventos
            conn.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    evento TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Valores por defecto en configuracion si no existen
            conn.execute("INSERT OR IGNORE INTO configuracion (clave, valor) VALUES ('start_text', ?)", (DEFAULT_START_TEXT,))
            # Eliminados los enlaces hardcodeados por defecto (ahora se crearán vía Join Request o /setlink)

            # Tabla de suscripciones Stripe ↔ Telegram
            conn.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_user_id       INTEGER NOT NULL,
                    stripe_customer_id     TEXT    NOT NULL UNIQUE,
                    stripe_subscription_id TEXT,
                    status                 TEXT    DEFAULT 'active',
                    created_at             TEXT    DEFAULT CURRENT_TIMESTAMP,
                    updated_at             TEXT    DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_subs_customer "
                "ON subscriptions(stripe_customer_id)"
            )

            # Tabla de persistencia para el borrado automático de Pick Premium a las 24h
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mensajes_pendientes_borrar (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER,
                    message_id INTEGER,
                    borrar_en INTEGER
                )
            """)

            conn.commit()
        logger.info("[DB] Base de datos y configuracion inicializadas.")

    # --- USUARIOS ---
    def registrar_usuario(self, user_id: int, username: str, first_name: str):
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO usuarios (telegram_user_id, username, first_name, fecha_registro, fecha_click_gratis)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT(telegram_user_id) DO UPDATE SET
                    fecha_click_gratis = CURRENT_TIMESTAMP,
                    username = excluded.username,
                    first_name = excluded.first_name
            """, (user_id, username or "", first_name or ""))
            conn.commit()

    def get_todos_usuarios(self) -> list:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT telegram_user_id FROM usuarios").fetchall()
        return [r["telegram_user_id"] for r in rows]

    def get_stats(self) -> dict:
        with self._get_conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
            en_embudo = conn.execute("SELECT COUNT(*) FROM usuarios WHERE estado = 'canal_gratis'").fetchone()[0]
            campanas = conn.execute("SELECT COUNT(*) FROM campanas").fetchone()[0]
        return {"total": total, "en_embudo": en_embudo, "campanas": campanas}

    # --- CONFIGURACION DINAMICA ---
    def get_config(self, clave: str, default: str = "") -> str:
        with self._get_conn() as conn:
            row = conn.execute("SELECT valor FROM configuracion WHERE clave = ?", (clave,)).fetchone()
        return row["valor"] if row and row["valor"] else default

    def set_config(self, clave: str, valor: str):
        with self._get_conn() as conn:
            conn.execute("INSERT OR REPLACE INTO configuracion (clave, valor) VALUES (?, ?)", (clave, valor))
            conn.commit()

    # --- CAMPAÑAS & LOGS ---
    def log_evento(self, user_id: int, evento: str):
        try:
            with self._get_conn() as conn:
                conn.execute("INSERT INTO logs (user_id, evento) VALUES (?, ?)", (user_id, evento))
                conn.commit()
        except Exception as e:
            logger.error(f"[DB] Error al registrar evento {evento}: {e}")

    def guardar_campana(self, titulo: str, mensaje: str, enviados: int):
        with self._get_conn() as conn:
            conn.execute("INSERT INTO campanas (titulo, mensaje, enviados) VALUES (?, ?, ?)", (titulo, mensaje, enviados))
            conn.commit()

    # ── Suscripciones Stripe ─────────────────────────────────────────────────

    def save_subscription(self, telegram_user_id: int, stripe_customer_id: str,
                          stripe_subscription_id: str, status: str = "active") -> None:
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO subscriptions
                    (telegram_user_id, stripe_customer_id, stripe_subscription_id, status)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(stripe_customer_id) DO UPDATE SET
                    stripe_subscription_id = excluded.stripe_subscription_id,
                    status                 = excluded.status,
                    updated_at             = CURRENT_TIMESTAMP
            """, (telegram_user_id, stripe_customer_id, stripe_subscription_id, status))
            conn.commit()

    def get_subscription_by_customer(self, stripe_customer_id: str) -> dict | None:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM subscriptions WHERE stripe_customer_id = ?",
                (stripe_customer_id,)
            ).fetchone()
        return dict(row) if row else None

    def update_subscription_status(self, stripe_customer_id: str, status: str) -> None:
        with self._get_conn() as conn:
            conn.execute("""
                UPDATE subscriptions
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE stripe_customer_id = ?
            """, (status, stripe_customer_id))
            conn.commit()

    def get_active_subscription(self, telegram_user_id: int) -> dict | None:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM subscriptions WHERE telegram_user_id = ? AND status = 'active'",
                (telegram_user_id,)
            ).fetchone()
        return dict(row) if row else None

    # ── Pick Premium Borrado Persistente ─────────────────────────────────────

    def guardar_borrado_pendiente(self, chat_id: int, message_id: int, borrar_en: int) -> None:
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO mensajes_pendientes_borrar (chat_id, message_id, borrar_en)
                VALUES (?, ?, ?)
            """, (chat_id, message_id, borrar_en))
            conn.commit()

    def obtener_borrados_pendientes(self) -> list:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM mensajes_pendientes_borrar").fetchall()
        return [dict(r) for r in rows]

    def eliminar_borrado_pendiente(self, chat_id: int, message_id: int) -> None:
        with self._get_conn() as conn:
            conn.execute("""
                DELETE FROM mensajes_pendientes_borrar
                WHERE chat_id = ? AND message_id = ?
            """, (chat_id, message_id))
            conn.commit()
