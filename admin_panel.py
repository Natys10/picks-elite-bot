import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import ADMIN_ID
from database import Database

logger = logging.getLogger(__name__)

# =============================================
#   PANEL DE ADMINISTRACIÓN Y DIFUSIONES (BROADCAST)
# =============================================

class AdminPanel:
    def __init__(self, db: Database):
        self.db = db

    def is_admin(self, user_id: int) -> bool:
        return user_id == ADMIN_ID

    def get_admin_menu(self) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton("📊 Estadísticas", callback_data="admin_stats")],
            [InlineKeyboardButton("✏️ Editar Mensaje Bienvenida", callback_data="admin_edit_start")],
            [InlineKeyboardButton("📢 Lanzar Difusión (Broadcast)", callback_data="admin_broadcast_info")],
            [InlineKeyboardButton("🔗 Editar Links (VIP / Gratis)", callback_data="admin_edit_links")],
        ]
        return InlineKeyboardMarkup(keyboard)

    async def show_admin_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id if update.effective_user else 0
        if not self.is_admin(uid):
            await update.message.reply_text("⛔ No tienes permisos de administración.")
            return

        await update.message.reply_text(
            "⚙️ *PANEL DE CONTROL — PICKS ÉLITE PLATFORM*\n\n"
            "Selecciona una opción para gestionar la plataforma:",
            parse_mode="Markdown",
            reply_markup=self.get_admin_menu()
        )

    async def broadcast_message(self, bot, text: str) -> int:
        """Envía un mensaje masivo a todos los usuarios registrados."""
        usuarios = self.db.get_todos_usuarios()
        enviados = 0

        for uid in usuarios:
            try:
                await bot.send_message(chat_id=uid, text=text, parse_mode="Markdown")
                enviados += 1
                await asyncio.sleep(0.05)  # Evita exceder limites de Telegram
            except Exception as e:
                logger.warning(f"[BROADCAST FAIL] user_id={uid}: {e}")

        self.db.guardar_campana("Difusion Manual", text, enviados)
        return enviados
