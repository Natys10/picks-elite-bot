import asyncio
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import Database
from config import (
    LINK_CANAL_GRATUITO,
    LINK_CANAL_VIP,
    TIEMPOS_EMBUDO,
    SCHEDULER_INTERVAL,
)

logger = logging.getLogger(__name__)

# =============================================
#   MÓDULO DE MARKETING — PICKS ÉLITE BOT
#   Gestiona el embudo de conversión completo:
#   Registro → Bienvenida → Follow-ups (24h/72h/7d)
# =============================================

class MarketingFunnel:
    """
    Clase principal del embudo de conversión.
    Separada de los handlers para mantener el código limpio.
    """

    def __init__(self, db: Database):
        self.db = db

    # ——— PASO 1: REGISTRO ———

    def registrar_entrada(self, user_id: int, username: str, first_name: str):
        """
        Registra al usuario cuando pulsa el botón Canal Gratuito.
        Si ya existe, solo actualiza la fecha de click.
        """
        self.db.registrar_usuario(user_id, username, first_name)
        self.db.log_evento(user_id, "click_canal_gratis")
        logger.info(f"[FUNNEL] Usuario entró al embudo: {user_id} (@{username})")

    # ——— PASO 2: BIENVENIDA ———

    async def enviar_bienvenida_canal_gratis(self, bot, query):
        """
        Muestra el mensaje de bienvenida del canal gratuito.
        Edita el mensaje del bot en lugar de enviar uno nuevo.
        Actualiza el estado del embudo a 'canal_gratis'.
        """
        user_id = query.from_user.id

        texto = (
            "⚽ *Bienvenido al Canal Gratuito.*\n\n"
            "Aquí recibirás diariamente:\n\n"
            "✅ Pronósticos gratuitos\n"
            "✅ Noticias importantes\n"
            "✅ Estadísticas\n"
            "✅ Resultados\n\n"
            "Además podrás conocer nuestro Canal VIP donde compartimos "
            "análisis más completos.\n\n"
            "Pulsa el botón para unirte."
        )
        teclado = [
            [InlineKeyboardButton("📢 Entrar al Canal Gratuito", url=LINK_CANAL_GRATUITO)],
            [InlineKeyboardButton("💎 Conocer Canal VIP", url=LINK_CANAL_VIP)],
            [InlineKeyboardButton("⬅️ Volver al menú", callback_data="inicio")],
        ]

        await query.edit_message_text(
            text=texto,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(teclado)
        )

        # Actualizar estado en la base de datos
        self.db.actualizar_estado(user_id, "canal_gratis")
        self.db.log_evento(user_id, "bienvenida_enviada")
        logger.info(f"[FUNNEL] Bienvenida enviada a: {user_id}")

    # ——— PASO 3: MENSAJES AUTOMÁTICOS ———

    async def _enviar_followup_24h(self, bot, user: dict):
        """Mensaje de seguimiento a las 24 horas."""
        first_name = user.get("first_name", "")
        user_id    = user["telegram_user_id"]

        texto = (
            f"Hola {first_name} 👋\n\n"
            "¿Ya viste los picks de hoy?\n\n"
            "Recuerda revisar el canal antes del primer partido."
        )
        teclado = [
            [InlineKeyboardButton("⚽ Abrir Canal", url=LINK_CANAL_GRATUITO)],
            [InlineKeyboardButton("💎 Conocer VIP",  url=LINK_CANAL_VIP)],
        ]
        await bot.send_message(
            chat_id=user_id,
            text=texto,
            reply_markup=InlineKeyboardMarkup(teclado)
        )
        self.db.marcar_enviado(user_id, "enviado_24h")
        self.db.log_evento(user_id, "followup_24h_enviado")
        logger.info(f"[FUNNEL] Follow-up 24h enviado a: {user_id}")

    async def _enviar_followup_72h(self, bot, user: dict):
        """Mensaje de seguimiento a las 72 horas."""
        first_name = user.get("first_name", "")
        user_id    = user["telegram_user_id"]

        texto = (
            f"Hola {first_name} 💎\n\n"
            "¿Sabías que en el Canal VIP publicamos análisis más completos?\n\n"
            "✔ Picks exclusivos\n"
            "✔ Gestión de bankroll\n"
            "✔ Más estadísticas"
        )
        teclado = [
            [InlineKeyboardButton("💎 Ver VIP",        url=LINK_CANAL_VIP)],
            [InlineKeyboardButton("⚽ Seguir Gratis", url=LINK_CANAL_GRATUITO)],
        ]
        await bot.send_message(
            chat_id=user_id,
            text=texto,
            reply_markup=InlineKeyboardMarkup(teclado)
        )
        self.db.marcar_enviado(user_id, "enviado_72h")
        self.db.log_evento(user_id, "followup_72h_enviado")
        logger.info(f"[FUNNEL] Follow-up 72h enviado a: {user_id}")

    async def _enviar_followup_7d(self, bot, user: dict):
        """Mensaje de seguimiento a los 7 días."""
        first_name = user.get("first_name", "")
        user_id    = user["telegram_user_id"]

        texto = (
            f"Hola {first_name} 🏆\n\n"
            "Gracias por formar parte de Picks Élite.\n\n"
            "Si deseas recibir nuestros mejores análisis puedes acceder al Canal VIP."
        )
        teclado = [
            [InlineKeyboardButton("💎 Quiero ser VIP", url=LINK_CANAL_VIP)],
        ]
        await bot.send_message(
            chat_id=user_id,
            text=texto,
            reply_markup=InlineKeyboardMarkup(teclado)
        )
        self.db.marcar_enviado(user_id, "enviado_7d")
        self.db.log_evento(user_id, "followup_7d_enviado")
        logger.info(f"[FUNNEL] Follow-up 7d enviado a: {user_id}")

    async def check_followups(self, bot):
        """
        Revisa la base de datos y envía los mensajes de seguimiento
        a los usuarios que ya cumplen el tiempo de espera.
        No bloquea el event loop.
        """
        logger.info("[SCHEDULER] Revisando follow-ups pendientes...")

        # ——— 24 horas ———
        for user in self.db.get_usuarios_para_followup("enviado_24h", TIEMPOS_EMBUDO["mensaje_24h"]):
            try:
                await self._enviar_followup_24h(bot, user)
            except Exception as e:
                logger.error(f"[ERROR] Follow-up 24h a {user['telegram_user_id']}: {e}")

        # ——— 72 horas ———
        for user in self.db.get_usuarios_para_followup("enviado_72h", TIEMPOS_EMBUDO["mensaje_72h"]):
            try:
                await self._enviar_followup_72h(bot, user)
            except Exception as e:
                logger.error(f"[ERROR] Follow-up 72h a {user['telegram_user_id']}: {e}")

        # ——— 7 días ———
        for user in self.db.get_usuarios_para_followup("enviado_7d", TIEMPOS_EMBUDO["mensaje_7d"]):
            try:
                await self._enviar_followup_7d(bot, user)
            except Exception as e:
                logger.error(f"[ERROR] Follow-up 7d a {user['telegram_user_id']}: {e}")

    async def iniciar_scheduler(self, bot):
        """
        Tarea de fondo que revisa follow-ups de forma periódica.
        Usa asyncio.sleep para no bloquear el event loop del bot.
        """
        logger.info(f"[SCHEDULER] Iniciado. Revisará cada {SCHEDULER_INTERVAL // 60} minutos.")
        while True:
            await asyncio.sleep(SCHEDULER_INTERVAL)
            await self.check_followups(bot)
