import os
import logging
import asyncio
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

from config import TOKEN, ADMIN_ID, CANAL_ID, CANAL_VIP_ID
from database import Database
from admin_panel import AdminPanel
import templates

# =============================================
#   PICKS ÉLITE PLATFORM — v3.0 (AUTOMATIZACIÓN & MARKETING)
# =============================================

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- INICIALIZAR MOTOR ---
db    = Database()
admin = AdminPanel(db)

# --- SERVIDOR DE SALUD (Railway) ---
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

# --- MENÚ PRINCIPAL DINÁMICO ---
def get_link_gratis():
    return db.get_config("link_gratis", "https://t.me/PicksElitePro")

def get_link_vip():
    return db.get_config("link_vip", "https://t.me/+ldrgDvLiC5NhOTRk")

def menu_principal():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚽ Canal Gratuito", url=get_link_gratis())],
        [InlineKeyboardButton("💎 Canal VIP",      callback_data="vip")],
        [InlineKeyboardButton("📊 Resultados",     callback_data="resultados")],
        [InlineKeyboardButton("ℹ️ Sobre nosotros", callback_data="about")],
    ])

def btn_volver():
    return [[InlineKeyboardButton("Volver al menú", callback_data="inicio")]]

# --- HANDLERS PÚBLICOS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user:
        db.registrar_usuario(user.id, user.username, user.first_name)
    
    start_text = db.get_config("start_text")
    await update.message.reply_text(
        start_text,
        parse_mode="Markdown",
        reply_markup=menu_principal()
    )

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(f"Tu ID de Telegram es: `{uid}`", parse_mode="Markdown")

# --- CALLBACKS DEL MENÚ ---
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
        "Para suscribirte contáctanos directamente 👇"
    )
    teclado = [
        [InlineKeyboardButton("✉️ Contactar para VIP", url=get_link_vip())],
        *btn_volver(),
    ]
    await query.edit_message_text(texto, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(teclado))

async def cb_resultados(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    texto = (
        "📊 *Historial de Resultados*\n\n"
        "🗓 *Julio 2026*\n"
        "✅ Picks acertados: 0\n"
        "❌ Picks fallados: 0\n\n"
        "_Canal recién lanzado. Los resultados se actualizarán cada día._"
    )
    teclado = [
        [InlineKeyboardButton("📢 Ver canal gratuito", url=get_link_gratis())],
        *btn_volver(),
    ]
    await query.edit_message_text(texto, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(teclado))

async def cb_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    texto = (
        "ℹ️ *Sobre Picks Élite*\n\n"
        "Canal de pronósticos de fútbol con enfoque *100% estadístico y analítico*.\n\n"
        "📌 Canal gratuito: @PicksElitePro\n"
        "💎 Canal VIP: Solo para suscriptores"
    )
    teclado = [
        [InlineKeyboardButton("📢 Unirse gratis", url=get_link_gratis())],
        *btn_volver(),
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

# --- PANEL DE ADMINISTRACIÓN (/admin) ---
async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await admin.show_admin_panel(update, context)

async def cmd_setstart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not admin.is_admin(update.effective_user.id):
        return
    if not context.args:
        await update.message.reply_text("📋 *Uso:* `/setstart Tu nuevo texto de bienvenida aquí`", parse_mode="Markdown")
        return
    nuevo_texto = " ".join(context.args)
    db.set_config("start_text", nuevo_texto)
    await update.message.reply_text("✅ *Mensaje de bienvenida actualizado exitosamente.*", parse_mode="Markdown")

async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not admin.is_admin(update.effective_user.id):
        return
    if not context.args:
        await update.message.reply_text("📋 *Uso:* `/broadcast Tu mensaje de difusión aquí`", parse_mode="Markdown")
        return
    mensaje = " ".join(context.args)
    await update.message.reply_text("🚀 *Iniciando difusión masiva...*", parse_mode="Markdown")
    enviados = await admin.broadcast_message(context.bot, mensaje)
    await update.message.reply_text(f"✅ *Difusión completada:* Enviado a `{enviados}` usuarios.", parse_mode="Markdown")

async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not admin.is_admin(update.effective_user.id):
        return
    st = db.get_stats()
    await update.message.reply_text(
        f"📊 *Estadísticas de la Plataforma*\n\n"
        f"👤 *Total usuarios registrados:* `{st['total']}`\n"
        f"⚽ *En embudo (Canal Gratis):* `{st['en_embudo']}`\n"
        f"📢 *Campañas lanzadas:* `{st['campanas']}`",
        parse_mode="Markdown"
    )

# --- COMANDOS DE PUBLICACIÓN (CON PLANTILLAS) ---

async def publicar_pick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    if not admin.is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Sin permiso de administración.")
        return

    full_text = update.message.text.strip()
    partes = full_text.split(maxsplit=1)
    content = partes[1].strip() if len(partes) > 1 else ""

    if not content:
        await update.message.reply_text(
            "📋 *Formato:* `/pick partido | apuesta | cuota | motivo`\n\n"
            "*Ejemplo:*\n`/pick Toluca U21 vs Pumas U21 | Ambos marcan: SÍ | 2.05 | Liga U21 = muchos goles.`",
            parse_mode="Markdown"
        )
        return

    try:
        p = content.split("|")
        partido = p[0].strip() if len(p) > 0 else ""
        apuesta = p[1].strip() if len(p) > 1 else ""
        cuota   = p[2].strip() if len(p) > 2 else ""
        motivo  = p[3].strip() if len(p) > 3 else ""

        msg = templates.format_pronostico_rapido(partido, apuesta, cuota, motivo)
        teclado = [[InlineKeyboardButton("👑 UNIRSE AL CANAL VIP", url=get_link_vip())]]

        await context.bot.send_message(
            chat_id=CANAL_ID,
            text=msg,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(teclado)
        )
        await update.message.reply_text("✅ ¡Pronóstico publicado en el canal exitosamente!")

    except Exception as e:
        await update.message.reply_text(f"❌ Error al publicar: `{e}`", parse_mode="Markdown")

async def publicar_directo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    if not admin.is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Sin permiso de administración.")
        return

    full_text = update.message.text.strip()
    partes = full_text.split(maxsplit=1)
    content = partes[1].strip() if len(partes) > 1 else ""

    if not content:
        await update.message.reply_text(
            "📋 *Formato:* `/directo partido | apuesta | periodo | cuota`\n\n"
            "*Ejemplo:*\n`/directo Toluca U21 vs Pumas U21 | Más de 0.5 goles | Primera Parte | 0.75`",
            parse_mode="Markdown"
        )
        return

    try:
        p = content.split("|")
        partido = p[0].strip() if len(p) > 0 else ""
        apuesta = p[1].strip() if len(p) > 1 else ""
        periodo = p[2].strip() if len(p) > 2 else "Primera Parte"
        cuota   = p[3].strip() if len(p) > 3 else ""

        msg = templates.format_directo(partido, apuesta, periodo, cuota)
        teclado = [[InlineKeyboardButton("👑 UNIRSE AL CANAL VIP", url=get_link_vip())]]

        await context.bot.send_message(
            chat_id=CANAL_ID,
            text=msg,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(teclado)
        )
        await update.message.reply_text("✅ ¡Apuesta en directo publicada en el canal exitosamente!")

    except Exception as e:
        await update.message.reply_text(f"❌ Error al publicar: `{e}`", parse_mode="Markdown")

WIN_BANNER_PATH = os.path.join(os.path.dirname(__file__), "win_banner.jpg")

async def publicar_win(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not admin.is_admin(update.effective_user.id): return
    try:
        full_text = update.message.text.strip()
        partes = full_text.split(maxsplit=1)
        content = partes[1].strip() if len(partes) > 1 else ""
        p = content.split("|")
        caption = templates.format_win(p[0].strip(), p[1].strip(), p[2].strip() if len(p) > 2 else "")
        teclado = [[InlineKeyboardButton("👑 UNIRSE AL CANAL VIP", url=get_link_vip())]]
        with open(WIN_BANNER_PATH, "rb") as foto:
            await context.bot.send_photo(
                chat_id=CANAL_ID,
                photo=foto,
                caption=caption,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(teclado)
            )
        await update.message.reply_text("✅ ¡WIN publicado con imagen en el canal!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: `{e}`", parse_mode="Markdown")

async def publicar_doble_win(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Publica doble WIN con imagen: /dwin partido | apuesta1 | apuesta2 | cuota1 | cuota2"""
    if not admin.is_admin(update.effective_user.id): return
    try:
        full_text = update.message.text.strip()
        partes = full_text.split(maxsplit=1)
        content = partes[1].strip() if len(partes) > 1 else ""
        p = content.split("|")
        partido  = p[0].strip() if len(p) > 0 else ""
        apuesta1 = p[1].strip() if len(p) > 1 else ""
        apuesta2 = p[2].strip() if len(p) > 2 else ""
        cuota1   = p[3].strip() if len(p) > 3 else ""
        cuota2   = p[4].strip() if len(p) > 4 else ""
        caption = templates.format_doble_win(partido, apuesta1, apuesta2, cuota1, cuota2)
        teclado = [[InlineKeyboardButton("👑 UNIRSE AL CANAL VIP", url=get_link_vip())]]
        with open(WIN_BANNER_PATH, "rb") as foto:
            await context.bot.send_photo(
                chat_id=CANAL_ID,
                photo=foto,
                caption=caption,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(teclado)
            )
        await update.message.reply_text("✅ ¡Doble WIN publicado con imagen! 🔥🔥")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: `{e}`", parse_mode="Markdown")

async def publicar_loss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not admin.is_admin(update.effective_user.id): return
    try:
        full_text = update.message.text.strip()
        partes = full_text.split(maxsplit=1)
        content = partes[1].strip() if len(partes) > 1 else ""
        p = content.split("|")
        msg = templates.format_loss(p[0].strip(), p[1].strip())
        await context.bot.send_message(chat_id=CANAL_ID, text=msg, parse_mode="Markdown")
        await update.message.reply_text("✅ LOSS publicado.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: `{e}`", parse_mode="Markdown")

# --- ARRANQUE DE LA PLATAFORMA ---
async def post_init(application: Application):
    await application.bot.delete_webhook(drop_pending_updates=True)
    await application.bot.set_my_commands([
        BotCommand("start", "Abrir menú principal"),
        BotCommand("admin", "Panel de administración"),
    ])
    # Asegurar que el link VIP siempre apunta al canal correcto
    if not db.get_config("link_vip"):
        db.set_config("link_vip", "https://t.me/+ldrgDvLiC5NhOTRk")
    logger.info("[OK] Links configurados correctamente.")

def main():
    threading.Thread(target=run_health_check, daemon=True).start()

    app = Application.builder().token(TOKEN).post_init(post_init).build()

    # Público
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id",    get_id))

    # Admin Panel
    app.add_handler(CommandHandler("admin",     cmd_admin))
    app.add_handler(CommandHandler("setstart",  cmd_setstart))
    app.add_handler(CommandHandler("broadcast", cmd_broadcast))
    app.add_handler(CommandHandler("stats",     cmd_stats))

    # Publicación con Plantillas
    app.add_handler(CommandHandler("pick",       publicar_pick))
    app.add_handler(CommandHandler("pickrapido", publicar_pick))
    app.add_handler(CommandHandler("directo",    publicar_directo))
    app.add_handler(CommandHandler("live",       publicar_directo))
    app.add_handler(CommandHandler("win",        publicar_win))
    app.add_handler(CommandHandler("dwin",       publicar_doble_win))
    app.add_handler(CommandHandler("loss",       publicar_loss))

    # Callbacks del menú
    app.add_handler(CallbackQueryHandler(cb_vip,        pattern="^vip$"))
    app.add_handler(CallbackQueryHandler(cb_resultados, pattern="^resultados$"))
    app.add_handler(CallbackQueryHandler(cb_about,      pattern="^about$"))
    app.add_handler(CallbackQueryHandler(cb_inicio,     pattern="^inicio$"))

    # Handler universal de texto fallback
    async def handle_text_fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message and update.message.text:
            txt = update.message.text.strip().lower()
            if txt.startswith("/directo") or txt.startswith("directo") or txt.startswith("/live"):
                await publicar_directo(update, context)
            elif txt.startswith("/pick") or txt.startswith("pick"):
                await publicar_pick(update, context)

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text_fallback))

    logger.info("[OK] Picks Elite Platform arrancada...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
