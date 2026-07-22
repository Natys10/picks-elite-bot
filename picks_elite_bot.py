import os
import logging
import asyncio
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters, ConversationHandler
)

from config import TOKEN, ADMIN_ID, CANAL_ID, CANAL_VIP_ID
from database import Database
from admin_panel import AdminPanel
import templates

# =============================================
#   PICKS ÉLITE PLATFORM — v4.0
#   Panel de administración completo
# =============================================

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

db    = Database()
admin = AdminPanel(db)

# Estados para ConversationHandler
ESPERANDO_PICK      = 1
ESPERANDO_DIRECTO   = 2
ESPERANDO_WIN       = 3
ESPERANDO_DWIN      = 4
ESPERANDO_LOSS      = 5
ESPERANDO_RESULTADO = 6
ESPERANDO_BROADCAST = 7
ESPERANDO_START_MSG = 8

# Banners por tipo de publicación
BANNERS = {
    "win":      os.path.join(os.path.dirname(__file__), "win_banner.jpg"),
    "pick":     os.path.join(os.path.dirname(__file__), "win_banner.jpg"),   # usar misma hasta tener banner pick
    "directo":  os.path.join(os.path.dirname(__file__), "win_banner.jpg"),
    "loss":     os.path.join(os.path.dirname(__file__), "win_banner.jpg"),
}

# =============================================
#   SERVIDOR DE SALUD (Railway)
# =============================================
def run_health_check():
    port = int(os.environ.get("PORT", 8080))
    class H(SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        def log_message(self, *a): pass
    try:
        HTTPServer(("", port), H).serve_forever()
    except Exception as e:
        logger.error(f"[HEALTH] {e}")

# =============================================
#   HELPERS
# =============================================
def get_link_gratis():
    return db.get_config("link_gratis", "https://t.me/PicksElitePro")

def get_link_vip():
    return db.get_config("link_vip", "https://t.me/+ldrgDvLiC5NhOTRk")

def menu_principal():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 ENTRAR AL CANAL GRATIS AQUÍ ⬇️", url=get_link_gratis())]
    ])

def btn_volver_admin():
    return [[InlineKeyboardButton("⬅️ Volver al panel", callback_data="admin_menu")]]

def btn_volver_menu():
    return [[InlineKeyboardButton("⬅️ Volver al menú", callback_data="inicio")]]

async def send_photo_canal(bot, canal, img_path, caption, keyboard=None):
    """Envía imagen+caption al canal dado."""
    markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    with open(img_path, "rb") as f:
        await bot.send_photo(
            chat_id=canal,
            photo=f,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=markup
        )

# =============================================
#   HANDLERS PÚBLICOS
# =============================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user:
        db.registrar_usuario(user.id, user.username, user.first_name)
        db.log_evento(user.id, "start")

    texto = (
        "✅ *SUSCRIPCIÓN ACTIVADA* ✅\n\n"
        "Ya puedes disfrutar de todos nuestros pronósticos y análisis estadísticos totalmente *GRATIS* ⬇️"
    )
    await update.message.reply_text(
        texto, parse_mode="Markdown", reply_markup=menu_principal()
    )

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(f"Tu ID de Telegram es: `{uid}`", parse_mode="Markdown")

# =============================================
#   CALLBACKS MENÚ PÚBLICO
# =============================================
async def cb_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    texto = (
        "💎 *Canal VIP — Picks Élite Premium*\n\n"
        "✅ 5 a 8 picks premium al día\n"
        "✅ Análisis H2H detallado\n"
        "✅ Gestión profesional de bankroll\n"
        "✅ Soporte directo con el analista\n\n"
        "💰 *Precio: €29 / mes*\n\n"
        "Para suscribirte accede ahora 👇"
    )
    teclado = [
        [InlineKeyboardButton("💎 Acceder al Canal VIP", url=get_link_vip())],
        *btn_volver_menu(),
    ]
    await query.edit_message_text(texto, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(teclado))

async def cb_resultados(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    st = db.get_stats()
    texto = (
        "📊 *Historial de Resultados*\n\n"
        f"✅ Picks acertados: `{st.get('wins', 0)}`\n"
        f"❌ Picks fallados: `{st.get('losses', 0)}`\n\n"
        "_Resultados actualizados en tiempo real._"
    )
    teclado = [
        [InlineKeyboardButton("📢 Ver canal gratuito", url=get_link_gratis())],
        *btn_volver_menu(),
    ]
    await query.edit_message_text(texto, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(teclado))

async def cb_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    texto = (
        "ℹ️ *Sobre Picks Élite*\n\n"
        "Canal de pronósticos con enfoque *100% estadístico y analítico*.\n\n"
        "📌 Canal gratuito: @PicksElitePro\n"
        "💎 Canal VIP: Solo para suscriptores"
    )
    teclado = [
        [InlineKeyboardButton("📢 Unirse gratis", url=get_link_gratis())],
        *btn_volver_menu(),
    ]
    await query.edit_message_text(texto, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(teclado))

async def cb_inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    start_text = db.get_config("start_text")
    try:
        await query.edit_message_text(start_text, parse_mode="Markdown", reply_markup=menu_principal())
    except Exception:
        await query.message.reply_text(start_text, parse_mode="Markdown", reply_markup=menu_principal())

# =============================================
#   PANEL DE ADMINISTRACIÓN
# =============================================
def get_panel_admin_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Estadísticas",          callback_data="admin_stats")],
        [InlineKeyboardButton("📣 Publicar en Canales",   callback_data="admin_publicar")],
        [InlineKeyboardButton("✏️ Mensaje de Bienvenida", callback_data="admin_edit_start")],
        [InlineKeyboardButton("📢 Difusión (Broadcast)",  callback_data="admin_broadcast_info")],
        [InlineKeyboardButton("🔗 Editar Links",          callback_data="admin_edit_links")],
    ])

async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not admin.is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Sin permisos.")
        return
    await update.message.reply_text(
        "⚙️ *PANEL DE CONTROL — PICKS ÉLITE*\n\nSelecciona una opción:",
        parse_mode="Markdown",
        reply_markup=get_panel_admin_markup()
    )

async def cb_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "⚙️ *PANEL DE CONTROL — PICKS ÉLITE*\n\nSelecciona una opción:",
        parse_mode="Markdown",
        reply_markup=get_panel_admin_markup()
    )

async def cb_admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not admin.is_admin(query.from_user.id): return
    st = db.get_stats()
    texto = (
        "📊 *Estadísticas de la Plataforma*\n\n"
        f"👤 Usuarios registrados: `{st['total']}`\n"
        f"⚽ En embudo canal gratis: `{st['en_embudo']}`\n"
        f"📣 Campañas lanzadas: `{st['campanas']}`"
    )
    await query.edit_message_text(texto, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(btn_volver_admin()))

async def cb_admin_publicar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Submenú de publicación de contenido."""
    query = update.callback_query
    await query.answer()
    if not admin.is_admin(query.from_user.id): return
    teclado = [
        [InlineKeyboardButton("⚡ Pick rápido",       callback_data="pub_pick")],
        [InlineKeyboardButton("🚨 En Directo / Live", callback_data="pub_directo")],
        [InlineKeyboardButton("🏆 WIN (1 pick)",      callback_data="pub_win")],
        [InlineKeyboardButton("💥 DOS VERDES (2 picks)", callback_data="pub_dwin")],
        [InlineKeyboardButton("📊 Resultado partido", callback_data="pub_resultado")],
        [InlineKeyboardButton("🔴 LOSS",              callback_data="pub_loss")],
        *btn_volver_admin(),
    ]
    await query.edit_message_text(
        "📣 *PUBLICAR EN CANALES*\n\n¿Qué quieres publicar?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(teclado)
    )

# — Instrucciones de cada tipo de publicación —
INSTRUCCIONES = {
    "pub_pick": (
        ESPERANDO_PICK,
        "⚡ *PICK RÁPIDO*\n\nEnvía los datos así:\n\n"
        "`partido | apuesta | cuota | motivo`\n\n"
        "*Ejemplo:*\n"
        "`Toluca vs Pumas | Ambos marcan: SÍ | 2.05 | Liga U21 = muchos goles`"
    ),
    "pub_directo": (
        ESPERANDO_DIRECTO,
        "🚨 *EN DIRECTO*\n\nEnvía los datos así:\n\n"
        "`partido | apuesta | período | cuota`\n\n"
        "*Ejemplo:*\n"
        "`Toluca vs Pumas | +0.5 goles | Primera Parte | 0.75`"
    ),
    "pub_win": (
        ESPERANDO_WIN,
        "🏆 *WIN (1 pick)*\n\nEnvía los datos así:\n\n"
        "`partido | apuesta | cuota`\n\n"
        "*Ejemplo:*\n"
        "`Toluca vs Pumas | Ambos marcan: SÍ | 2.05`"
    ),
    "pub_dwin": (
        ESPERANDO_DWIN,
        "💥 *DOS VERDES*\n\nEnvía los datos así:\n\n"
        "`partido | apuesta1 | apuesta2 | cuota1 | cuota2`\n\n"
        "*Ejemplo:*\n"
        "`Toluca vs Pumas | +0.5 goles 1T | Ambos marcan: SÍ | 0.75 | 2.05`"
    ),
    "pub_resultado": (
        ESPERANDO_RESULTADO,
        "📊 *RESULTADO DE PARTIDO*\n\nEnvía los datos así:\n\n"
        "`partido | resultado | pick1 | pick2 | detalle`\n\n"
        "*Ejemplo:*\n"
        "`Toluca vs Pumas | 1-1 | +0.5 goles 1T GANADO | Ambos marcan GANADO | Partido muy movido`"
    ),
    "pub_loss": (
        ESPERANDO_LOSS,
        "🔴 *LOSS*\n\nEnvía los datos así:\n\n"
        "`partido | apuesta`\n\n"
        "*Ejemplo:*\n"
        "`Toluca vs Pumas | Victoria Toluca`"
    ),
}

async def cb_pub_tipo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja cualquier botón de tipo de publicación."""
    query = update.callback_query
    await query.answer()
    if not admin.is_admin(query.from_user.id): return
    data = query.data
    if data not in INSTRUCCIONES: return
    estado, instruccion = INSTRUCCIONES[data]
    context.user_data["pub_estado"] = estado
    context.user_data["pub_tipo"]   = data
    await query.edit_message_text(
        instruccion + "\n\n_O envía /cancelar para salir._",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ Cancelar", callback_data="admin_publicar")
        ]])
    )

async def cb_admin_edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not admin.is_admin(query.from_user.id): return
    context.user_data["pub_estado"] = ESPERANDO_START_MSG
    await query.edit_message_text(
        "✏️ *EDITAR MENSAJE DE BIENVENIDA*\n\n"
        "Escribe el nuevo texto de bienvenida.\n"
        "Puedes usar *negrita*, _cursiva_ y emojis.\n\n"
        "_Envía /cancelar para salir._",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ Cancelar", callback_data="admin_menu")
        ]])
    )

async def cb_admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not admin.is_admin(query.from_user.id): return
    context.user_data["pub_estado"] = ESPERANDO_BROADCAST
    usuarios = db.get_stats()["total"]
    await query.edit_message_text(
        f"📢 *DIFUSIÓN MASIVA*\n\n"
        f"Se enviará a *{usuarios} usuarios* registrados.\n\n"
        "Escribe el mensaje que quieres difundir:\n\n"
        "_Envía /cancelar para salir._",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ Cancelar", callback_data="admin_menu")
        ]])
    )

async def cb_admin_edit_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not admin.is_admin(query.from_user.id): return
    link_g = get_link_gratis()
    link_v = get_link_vip()
    await query.edit_message_text(
        f"🔗 *LINKS ACTUALES*\n\n"
        f"⚽ Canal Gratis: `{link_g}`\n"
        f"💎 Canal VIP: `{link_v}`\n\n"
        "Para cambiar usa estos comandos:\n"
        "`/setlink gratis https://t.me/...`\n"
        "`/setlink vip https://t.me/...`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(btn_volver_admin())
    )

# =============================================
#   MANEJADOR DE TEXTO ENTRANTE (publicaciones)
# =============================================
async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    uid = update.effective_user.id
    if not admin.is_admin(uid): return

    estado = context.user_data.get("pub_estado")
    text   = update.message.text.strip()

    # Cancelar
    if text.lower() in ["/cancelar", "cancelar"]:
        context.user_data.pop("pub_estado", None)
        context.user_data.pop("pub_tipo", None)
        await update.message.reply_text("❌ Operación cancelada.", reply_markup=get_panel_admin_markup())
        return

    if estado == ESPERANDO_START_MSG:
        db.set_config("start_text", text)
        context.user_data.pop("pub_estado", None)
        await update.message.reply_text("✅ Mensaje de bienvenida actualizado.", reply_markup=get_panel_admin_markup())

    elif estado == ESPERANDO_BROADCAST:
        context.user_data.pop("pub_estado", None)
        await update.message.reply_text("🚀 Enviando difusión...")
        enviados = await admin.broadcast_message(context.bot, text)
        await update.message.reply_text(f"✅ Difusión enviada a `{enviados}` usuarios.", parse_mode="Markdown")

    elif estado == ESPERANDO_PICK:
        context.user_data.pop("pub_estado", None)
        try:
            p = text.split("|")
            msg = templates.format_pronostico_rapido(
                p[0].strip(), p[1].strip(),
                p[2].strip() if len(p) > 2 else "",
                p[3].strip() if len(p) > 3 else ""
            )
            teclado = [[InlineKeyboardButton("👑 CANAL VIP", url=get_link_vip())]]
            await send_photo_canal(context.bot, CANAL_ID, BANNERS["pick"], msg, teclado)
            await update.message.reply_text("✅ ¡Pick publicado en el canal gratuito!", reply_markup=get_panel_admin_markup())
        except Exception as e:
            await update.message.reply_text(f"❌ Error: `{e}`", parse_mode="Markdown")

    elif estado == ESPERANDO_DIRECTO:
        context.user_data.pop("pub_estado", None)
        try:
            p = text.split("|")
            msg = templates.format_directo(
                p[0].strip(), p[1].strip(),
                p[2].strip() if len(p) > 2 else "Primera Parte",
                p[3].strip() if len(p) > 3 else ""
            )
            teclado = [[InlineKeyboardButton("👑 CANAL VIP", url=get_link_vip())]]
            await send_photo_canal(context.bot, CANAL_ID, BANNERS["directo"], msg, teclado)
            await update.message.reply_text("✅ ¡Apuesta en directo publicada!", reply_markup=get_panel_admin_markup())
        except Exception as e:
            await update.message.reply_text(f"❌ Error: `{e}`", parse_mode="Markdown")

    elif estado == ESPERANDO_WIN:
        context.user_data.pop("pub_estado", None)
        try:
            p = text.split("|")
            msg = templates.format_win(
                p[0].strip(), p[1].strip(),
                p[2].strip() if len(p) > 2 else ""
            )
            teclado = [[InlineKeyboardButton("👑 CANAL VIP", url=get_link_vip())]]
            await send_photo_canal(context.bot, CANAL_ID, BANNERS["win"], msg, teclado)
            await update.message.reply_text("✅ ¡WIN publicado con imagen!", reply_markup=get_panel_admin_markup())
        except Exception as e:
            await update.message.reply_text(f"❌ Error: `{e}`", parse_mode="Markdown")

    elif estado == ESPERANDO_DWIN:
        context.user_data.pop("pub_estado", None)
        try:
            p = text.split("|")
            msg = templates.format_doble_win(
                p[0].strip(),
                p[1].strip() if len(p) > 1 else "",
                p[2].strip() if len(p) > 2 else "",
                p[3].strip() if len(p) > 3 else "",
                p[4].strip() if len(p) > 4 else ""
            )
            teclado = [[InlineKeyboardButton("👑 CANAL VIP", url=get_link_vip())]]
            await send_photo_canal(context.bot, CANAL_ID, BANNERS["win"], msg, teclado)
            await update.message.reply_text("✅ ¡Doble WIN publicado con imagen! 🔥", reply_markup=get_panel_admin_markup())
        except Exception as e:
            await update.message.reply_text(f"❌ Error: `{e}`", parse_mode="Markdown")

    elif estado == ESPERANDO_RESULTADO:
        context.user_data.pop("pub_estado", None)
        try:
            p = text.split("|")
            partido  = p[0].strip()
            resultado = p[1].strip() if len(p) > 1 else ""
            pick1    = p[2].strip() if len(p) > 2 else ""
            pick2    = p[3].strip() if len(p) > 3 else ""
            detalle  = p[4].strip() if len(p) > 4 else ""
            msg = templates.format_resultado(partido, resultado, pick1, pick2, detalle)
            teclado = [[InlineKeyboardButton("👑 QUIERO EL CANAL VIP", url=get_link_vip())]]
            await send_photo_canal(context.bot, CANAL_ID, BANNERS["win"], msg, teclado)
            await update.message.reply_text("✅ ¡Resultado publicado!", reply_markup=get_panel_admin_markup())
        except Exception as e:
            await update.message.reply_text(f"❌ Error: `{e}`", parse_mode="Markdown")

    elif estado == ESPERANDO_LOSS:
        context.user_data.pop("pub_estado", None)
        try:
            p = text.split("|")
            msg = templates.format_loss(p[0].strip(), p[1].strip() if len(p) > 1 else "")
            await context.bot.send_message(chat_id=CANAL_ID, text=msg, parse_mode="Markdown")
            await update.message.reply_text("✅ LOSS publicado.", reply_markup=get_panel_admin_markup())
        except Exception as e:
            await update.message.reply_text(f"❌ Error: `{e}`", parse_mode="Markdown")

# =============================================
#   COMANDOS ADMIN ADICIONALES
# =============================================
async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not admin.is_admin(update.effective_user.id): return
    st = db.get_stats()
    await update.message.reply_text(
        f"📊 *Estadísticas*\n\n"
        f"👤 Usuarios: `{st['total']}`\n"
        f"⚽ En embudo: `{st['en_embudo']}`\n"
        f"📣 Campañas: `{st['campanas']}`",
        parse_mode="Markdown"
    )

async def cmd_setlink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not admin.is_admin(update.effective_user.id): return
    if len(context.args) < 2:
        await update.message.reply_text("Uso: `/setlink gratis|vip https://t.me/...`", parse_mode="Markdown")
        return
    tipo, url = context.args[0].lower(), context.args[1]
    if tipo == "gratis":
        db.set_config("link_gratis", url)
        await update.message.reply_text(f"✅ Link canal gratuito actualizado: `{url}`", parse_mode="Markdown")
    elif tipo == "vip":
        db.set_config("link_vip", url)
        await update.message.reply_text(f"✅ Link canal VIP actualizado: `{url}`", parse_mode="Markdown")
    else:
        await update.message.reply_text("Tipo inválido. Usa `gratis` o `vip`.", parse_mode="Markdown")

# =============================================
#   ARRANQUE
# =============================================
async def post_init(application: Application):
    await application.bot.delete_webhook(drop_pending_updates=True)
    # Limpiar comandos viejos cacheados antes de registrar los nuevos
    await application.bot.delete_my_commands()
    await application.bot.set_my_commands([
        BotCommand("start",  "Abrir menú principal"),
        BotCommand("admin",  "Panel de administración"),
        BotCommand("stats",  "Ver estadísticas"),
    ])
    # Forzar siempre el link correcto (por si Railway tiene el viejo en su BD)
    db.set_config("link_vip",    "https://t.me/+ldrgDvLiC5NhOTRk")
    db.set_config("link_gratis", "https://t.me/PicksElitePro")
    logger.info("[OK] Picks Elite Platform v4.0 lista.")

def main():
    threading.Thread(target=run_health_check, daemon=True).start()

    app = Application.builder().token(TOKEN).post_init(post_init).build()

    # Público
    app.add_handler(CommandHandler("start",  start))
    app.add_handler(CommandHandler("id",     get_id))

    # Admin comandos directos
    app.add_handler(CommandHandler("admin",  cmd_admin))
    app.add_handler(CommandHandler("stats",  cmd_stats))
    app.add_handler(CommandHandler("setlink", cmd_setlink))

    # Callbacks menú público
    app.add_handler(CallbackQueryHandler(cb_vip,        pattern="^vip$"))
    app.add_handler(CallbackQueryHandler(cb_resultados, pattern="^resultados$"))
    app.add_handler(CallbackQueryHandler(cb_about,      pattern="^about$"))
    app.add_handler(CallbackQueryHandler(cb_inicio,     pattern="^inicio$"))

    # Callbacks panel admin
    app.add_handler(CallbackQueryHandler(cb_admin_menu,      pattern="^admin_menu$"))
    app.add_handler(CallbackQueryHandler(cb_admin_stats,     pattern="^admin_stats$"))
    app.add_handler(CallbackQueryHandler(cb_admin_publicar,  pattern="^admin_publicar$"))
    app.add_handler(CallbackQueryHandler(cb_admin_edit_start,pattern="^admin_edit_start$"))
    app.add_handler(CallbackQueryHandler(cb_admin_broadcast, pattern="^admin_broadcast_info$"))
    app.add_handler(CallbackQueryHandler(cb_admin_edit_links,pattern="^admin_edit_links$"))

    # Callbacks submenú publicación
    app.add_handler(CallbackQueryHandler(cb_pub_tipo, pattern="^pub_"))

    # Manejador de texto (publicaciones y ediciones)
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text_input))

    logger.info("[OK] Picks Elite Platform arrancada en modo POLLING...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
