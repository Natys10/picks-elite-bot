import os

# =============================================
#   CONFIGURACIÓN GLOBAL — PICKS ÉLITE BOT
# =============================================

TOKEN = os.environ.get("BOT_TOKEN", "8915840915:AAFWX7lh3wxO3QKWutoCMdYB7l-TcJ5aQJQ")
ADMIN_ID = 8516113803
CANAL_ID     = "@PicksElitePro"          # Canal gratuito
CANAL_VIP_ID = -1004381972016            # Canal VIP (privado)
LINK_CANAL_GRATUITO = "https://t.me/PicksElitePro"
LINK_CANAL_VIP = "https://t.me/+ldrgDvLiC5NhOTRk"

DB_PATH = os.environ.get("DB_PATH", "picks_elite.db")

DEFAULT_START_TEXT = """👑 *¡Bienvenido a Picks Élite!*

⚽ Bienvenido a una comunidad donde el análisis está por encima de la suerte.

Aquí encontrarás:
📊 Pronósticos gratuitos
📈 Estadísticas transparentes
💎 Acceso exclusivo al Canal VIP

🎯 Nuestro objetivo es ayudarte a tomar decisiones más informadas.
"""
