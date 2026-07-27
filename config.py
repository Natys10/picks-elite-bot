import os

# =============================================
#   CONFIGURACIÓN GLOBAL — PICKS ÉLITE BOT
# =============================================

TOKEN = os.environ.get("BOT_TOKEN", "8915840915:AAFWX7lh3wxO3QKWutoCMdYB7l-TcJ5aQJQ")
ADMIN_ID = 8516113803
canal_id_env = os.environ.get("CANAL_ID")
if not canal_id_env:
    raise RuntimeError("\n❌ ERROR CRÍTICO: La variable de entorno CANAL_ID no está configurada.\nDebes configurarla en Railway con el ID numérico real del canal privado.\nEl bot no puede iniciar.\n")
CANAL_ID = int(canal_id_env)

CANAL_VIP_ID = int(os.environ.get("CANAL_VIP_ID", -1004381972016)) # Canal VIP (privado)

DB_PATH = os.environ.get("DB_PATH", "picks_elite.db")

DEFAULT_START_TEXT = """👑 *¡Bienvenido a Picks Élite!*

⚽ Bienvenido a una comunidad donde el análisis está por encima de la suerte.

Aquí encontrarás:
📊 Pronósticos gratuitos
📈 Estadísticas transparentes
💎 Acceso exclusivo al Canal VIP

🎯 Nuestro objetivo es ayudarte a tomar decisiones más informadas.
"""
