import os

# =============================================
#   CONFIGURACIÓN GLOBAL — PICKS ÉLITE BOT
# =============================================

# ——— Token del bot (puede venir de variable de entorno) ———
TOKEN = os.environ.get("BOT_TOKEN", "8915840915:AAFWX7lh3wxO3QKWutoCMdYB7l-TcJ5aQJQ")

# ——— ID del administrador (dueño del bot) ———
ADMIN_ID = 8516113803

# ——— Canal ———
CANAL_ID            = "@PicksElitePro"
LINK_CANAL_GRATUITO = "https://t.me/PicksElitePro"
LINK_CANAL_VIP      = "https://t.me/PicksEliteProBot"

# ——— Base de datos SQLite ———
DB_PATH = os.environ.get("DB_PATH", "picks_elite.db")

# ——— Tiempos del embudo de conversión (en segundos) ———
TIEMPOS_EMBUDO = {
    "mensaje_24h": 24 * 3600,       # 24 horas
    "mensaje_72h": 72 * 3600,       # 72 horas
    "mensaje_7d":  7 * 24 * 3600,   # 7 días
}

# ——— Intervalo del scheduler (cada cuánto revisa los follow-ups) ———
SCHEDULER_INTERVAL = 1800  # 30 minutos
