import os

# =============================================
#   CONFIGURACIÓN GLOBAL — PICKS ÉLITE BOT
# =============================================

TOKEN = os.environ.get("BOT_TOKEN", "8915840915:AAFWX7lh3wxO3QKWutoCMdYB7l-TcJ5aQJQ")
ADMIN_ID = 8516113803

valor = os.environ.get("CANAL_ID")

if valor is None:
    print("⚠️ CANAL_ID no configurado. Se usará -1 temporalmente.")
    CANAL_ID = -1
else:
    CANAL_ID = int(valor)

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
