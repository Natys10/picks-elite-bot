import sqlite3
import logging
from config import DB_PATH

logger = logging.getLogger(__name__)

# =============================================
#   MÓDULO DE BASE DE DATOS — PICKS ÉLITE BOT
#   Motor: SQLite
#   Tablas: usuarios, logs
# =============================================

class Database:
    """
    Gestiona todas las operaciones de base de datos del bot.
    Usa SQLite para evitar dependencias externas.
    """

    def __init__(self):
        self.db_path = DB_PATH
        self.init_db()

    def _get_conn(self) -> sqlite3.Connection:
        """Crea y retorna una conexión a la base de datos."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Permite acceder a columnas por nombre
        return conn

    def init_db(self):
        """Crea las tablas si no existen. Se llama al arrancar el bot."""
        with self._get_conn() as conn:
            # Tabla principal de usuarios del embudo
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    telegram_user_id     INTEGER PRIMARY KEY,
                    username             TEXT,
                    first_name           TEXT,
                    fecha_registro       DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_click_canal_gratis DATETIME,
                    estado_embudo        TEXT DEFAULT 'nuevo',
                    enviado_24h          BOOLEAN DEFAULT 0,
                    enviado_72h          BOOLEAN DEFAULT 0,
                    enviado_7d           BOOLEAN DEFAULT 0
                )
            """)
            # Tabla de log de eventos
            conn.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id   INTEGER,
                    evento    TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        logger.info("[DB] Base de datos inicializada correctamente.")

    # ——— USUARIOS ———

    def registrar_usuario(self, user_id: int, username: str, first_name: str):
        """
        Inserta un usuario nuevo o actualiza la fecha de click
        si ya existe en la base de datos.
        """
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO usuarios
                    (telegram_user_id, username, first_name, fecha_registro, fecha_click_canal_gratis)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT(telegram_user_id) DO UPDATE SET
                    fecha_click_canal_gratis = CURRENT_TIMESTAMP,
                    username   = excluded.username,
                    first_name = excluded.first_name
            """, (user_id, username or "", first_name or ""))
            conn.commit()
        logger.info(f"[DB] Usuario registrado/actualizado: {user_id} (@{username})")

    def actualizar_estado(self, user_id: int, estado: str):
        """Actualiza el estado del embudo de un usuario."""
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE usuarios SET estado_embudo = ? WHERE telegram_user_id = ?",
                (estado, user_id)
            )
            conn.commit()

    def marcar_enviado(self, user_id: int, campo: str):
        """
        Marca un mensaje de seguimiento como enviado.
        campo puede ser: 'enviado_24h', 'enviado_72h', 'enviado_7d'
        """
        campos_permitidos = {"enviado_24h", "enviado_72h", "enviado_7d"}
        if campo not in campos_permitidos:
            logger.error(f"[DB] Campo inválido: {campo}")
            return
        with self._get_conn() as conn:
            conn.execute(
                f"UPDATE usuarios SET {campo} = 1 WHERE telegram_user_id = ?",
                (user_id,)
            )
            conn.commit()

    def get_usuarios_para_followup(self, campo_enviado: str, segundos_espera: int) -> list:
        """
        Devuelve usuarios que:
        - Están en estado 'canal_gratis'
        - No han recibido el mensaje indicado (campo_enviado = 0)
        - Han pasado los segundos_espera desde que hicieron click en el canal
        """
        with self._get_conn() as conn:
            rows = conn.execute(f"""
                SELECT * FROM usuarios
                WHERE {campo_enviado} = 0
                AND estado_embudo = 'canal_gratis'
                AND fecha_click_canal_gratis <= datetime('now', '-{segundos_espera} seconds')
            """).fetchall()
        return [dict(row) for row in rows]

    def obtener_usuario(self, user_id: int) -> dict | None:
        """Obtiene los datos completos de un usuario."""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM usuarios WHERE telegram_user_id = ?", (user_id,)
            ).fetchone()
        return dict(row) if row else None

    # ——— LOGS ———

    def log_evento(self, user_id: int, evento: str):
        """Registra un evento en la tabla de logs."""
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO logs (user_id, evento) VALUES (?, ?)",
                (user_id, evento)
            )
            conn.commit()
        logger.info(f"[LOG] user_id={user_id} | evento={evento}")
