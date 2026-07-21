import os
import logging
import asyncio
import sqlite3
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# =============================================
#   PICKS ELITE BOT — v2.0 (todo en un archivo)
# =============================================

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- CONFIGURACION ---
TOKEN    = "8915840915:AAFWX7lh3wxO3QKWutoCMdYB7l-TcJ5aQJQ"
ADMIN_ID = 8516113803
CANAL_ID = "@PicksElitePro"
LINK_GRATUITO = "https://t.me/PicksElitePro"
LINK_VIP      = "https://t.me/PicksEliteProBot"
DB_PATH  = "picks_elite.db"

# --- BASE DE DATOS ---
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id   INTEGER,
                evento    TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    logger.info("[DB] Base de datos lista.")

def registrar_usuario(user_id, username, first_name):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO usuarios (telegram_user_id, username, first_name, fecha_registro, fecha_click_gratis)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT(telegram_user_id) DO UPDATE SET
                fecha_click_gratis = CURRENT_TIMESTAMP,
                username = excluded.username,
                first_name = excluded.first_name
        """, (user_id, username or "", first_name or ""))
        conn.execute("INSERT INTO logs (user_id, evento) VALUES (?, ?)", (user_id, "click_canal_gratis"))
        conn.commit()
    logger.info(f"[DB] Usuario registrado: {user_id} (@{username})")

def get_stats():
    with sqlite3.connect(DB_PATH) as conn:
        total = conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
        en_embudo = conn.execute("SELECT COUNT(*) FROM usuarios WHERE estado = 'canal_gratis'").fetchone()[0]
    return total, en_embudo

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

# --- MENU ---
def menu_principal():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚽ Canal Gratuito", url=LINK_GRATUITO)],
        [InlineKeyboardButton("💎 Canal VIP",      callback_data="vip")],
        [InlineKeyboardButton("📊 Resultados",     callback_data="resultados")],
        [InlineKeyboardButton("ℹ️ Sobre nosotros", callback_data="about")],
    ])

def btn_volver():
    return [[InlineKeyboardButton("Volver al menu", callback_data="inicio")]]

# --- HANDLERS PUBLICOS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"[CMD] /start de {update.effective_user.id}")
    await update.message.reply_text(
        "Bienvenido a Picks Elite.\n\nSelecciona una opcion:",
        reply_markup=menu_principal()
    )

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    logger.info(f"[CMD] /id de {uid}")
    await update.message.reply_text(f"Tu ID es: {uid}")

# --- CALLBACKS DEL MENU ---
async def cb_canal_gratis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    logger.info(f"[BTN] canal_gratis de {user.id}")

    # Registrar en la base de datos
    registrar_usuario(user.id, user.username, user.first_name)

    # Actualizar estado
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE usuarios SET estado = 'canal_gratis' WHERE telegram_user_id = ?", (user.id,))
        conn.commit()

    texto = (
        "Bienvenido al Canal Gratuito.\n\n"
        "Aqui recibiras diariamente:\n\n"
        "Pronosticos gratuitos\n"
        "Noticias importantes\n"
        "Estadisticas\n"
        "Resultados\n\n"
        "Pulsa el boton para unirte."
    )
    teclado = [
        [InlineKeyboardButton("Entrar al Canal Gratuito", url=LINK_GRATUITO)],
        [InlineKeyboardButton("Conocer Canal VIP",        url=LINK_VIP)],
        *btn_volver(),
    ]
    await query.edit_message_text(texto, reply_markup=InlineKeyboardMarkup(teclado))

async def cb_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    texto = (
        "Canal VIP - Picks Elite Premium\n\n"
        "5 a 8 picks premium al dia\n"
        "Analisis H2H detallado\n"
        "Gestion profesional de bankroll\n"
        "Soporte directo con el analista\n\n"
        "Precio: 29 EUR / mes\n\n"
        "Contacta para suscribirte."
    )
    teclado = [
        [InlineKeyboardButton("Contactar para VIP", url=LINK_VIP)],
        *btn_volver(),
    ]
    await query.edit_message_text(texto, reply_markup=InlineKeyboardMarkup(teclado))

async def cb_resultados(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    texto = (
        "Historial de Resultados\n\n"
        "Julio 2026\n"
        "Picks acertados: 0\n"
        "Picks fallados: 0\n"
        "Canal recien lanzado.\n"
        "Los resultados se actualizaran cada dia."
    )
    teclado = [
        [InlineKeyboardButton("Ver canal gratuito", url=LINK_GRATUITO)],
        *btn_volver(),
    ]
    await query.edit_message_text(texto, reply_markup=InlineKeyboardMarkup(teclado))

async def cb_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    texto = (
        "Sobre Picks Elite\n\n"
        "Canal de pronosticos de futbol con enfoque estadistico y analitico.\n\n"
        "Canal gratuito: @PicksElitePro\n"
        "Canal VIP: Solo para suscriptores"
    )
    teclado = [
        [InlineKeyboardButton("Unirse gratis", url=LINK_GRATUITO)],
        *btn_volver(),
    ]
    await query.edit_message_text(texto, reply_markup=InlineKeyboardMarkup(teclado))

async def cb_inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.edit_message_text(
            "Bienvenido a Picks Elite.\n\nSelecciona una opcion:",
            reply_markup=menu_principal()
        )
    except Exception:
        await query.message.reply_text(
            "Bienvenido a Picks Elite.\n\nSelecciona una opcion:",
            reply_markup=menu_principal()
        )

# --- COMANDOS ADMIN ---
def es_admin(update: Update) -> bool:
    uid = update.effective_user.id if update.effective_user else 0
    logger.info(f"[ADMIN CHECK] user_id={uid} ADMIN_ID={ADMIN_ID} resultado={uid == ADMIN_ID}")
    return uid == ADMIN_ID

async def publicar_pick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    uid = update.effective_user.id if update.effective_user else 0
    logger.info(f"[PICK] Recibido de {uid}: {update.message.text}")

    # Enviar acuse de recibo inmediato
    try:
        await update.message.reply_text("🔄 Procesando pick...")
    except Exception as err:
        logger.error(f"[REPLY ERROR] {err}")

    if not es_admin(update):
        await update.message.reply_text(f"⛔ Sin permiso. Tu ID={uid}, Admin ID={ADMIN_ID}")
        return

    # Extraer texto despues de /pick
    full_text = update.message.text.strip()
    # Remover /pick o /pick@BotName
    if full_text.startswith("/pick"):
        partes_cmd = full_text.split(maxsplit=1)
        content = partes_cmd[1].strip() if len(partes_cmd) > 1 else ""
    else:
        content = full_text

    if not content:
        await update.message.reply_text(
            "📋 *Formato:* /pick partido | apuesta | cuota | liga | hora\n\n"
            "*Ejemplo:*\n`/pick Real Madrid vs Barcelona | Ambos Marcan | 1.80 | LaLiga | 21:00h`",
            parse_mode="Markdown"
        )
        return

    try:
        p = content.split("|")
        partido = p[0].strip() if len(p) > 0 else ""
        apuesta = p[1].strip() if len(p) > 1 else ""
        cuota   = p[2].strip() if len(p) > 2 else ""
        motivo  = p[3].strip() if len(p) > 3 else ""

        if not partido or not apuesta:
            await update.message.reply_text("❌ Falta el partido o el pronóstico. Usa las barras | para separar.")
            return

        motivo_seccion = f"\nMotivo: {motivo}\n" if motivo else ""

        # Formato exacto solicitado por la usuaria
        msg = (
            f"*PRONÓSTICO RÁPIDO*\n\n"
            f"*{partido}*\n"
            f"➡️ {apuesta}\n"
            f"➡️ Cuota: {cuota}\n"
            f"{motivo_seccion}\n"
            f"Suerte 🍀\n"
            f"Apuesta con cabeza"
        )
        teclado = [[InlineKeyboardButton("👑 UNIRSE AL CANAL VIP", url=LINK_VIP)]]
        await context.bot.send_message(
            chat_id=CANAL_ID,
            text=msg,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(teclado)
        )
        await update.message.reply_text("✅ ¡Pronóstico publicado en el canal exitosamente!")
        logger.info(f"[PICK SUCCESS] Publicado: {partido}")

    except Exception as e:
        logger.error(f"[PICK ERROR] {e}")
        await update.message.reply_text(f"❌ Error al publicar en el canal: `{e}`", parse_mode="Markdown")


# ——— /pickrapido partido | apuesta | cuota | motivo ———
async def publicar_pick_rapido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await publicar_pick(update, context)

async def publicar_win(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not es_admin(update):
        await update.message.reply_text("Sin permiso.")
        return
    try:
        p = " ".join(context.args).split("|")
        partido = p[0].strip()
        apuesta = p[1].strip()
        cuota   = p[2].strip() if len(p) > 2 else ""
        msg = (
            f"VERDE - PICKS ELITE\n\n"
            f"Evento: {partido}\n"
            f"Pronostico: {apuesta}\n"
            f"{'Cuota cobrada: ' + cuota if cuota else ''}\n\n"
            f"Cobrada otra apuesta gratuita. Felicidades."
        )
        await context.bot.send_message(
            chat_id=CANAL_ID, text=msg,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Quiero el VIP", url=LINK_VIP)]])
        )
        await update.message.reply_text("WIN publicado.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def publicar_loss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not es_admin(update):
        await update.message.reply_text("Sin permiso.")
        return
    try:
        p = " ".join(context.args).split("|")
        partido = p[0].strip()
        apuesta = p[1].strip()
        msg = (
            f"ROJO - PICKS ELITE\n\n"
            f"Evento: {partido}\n"
            f"Pronostico: {apuesta}\n\n"
            f"Transparencia total. Seguimos trabajando para el proximo verde."
        )
        await context.bot.send_message(chat_id=CANAL_ID, text=msg)
        await update.message.reply_text("LOSS publicado.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def publicar_aviso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not es_admin(update):
        await update.message.reply_text("Sin permiso.")
        return
    if not context.args:
        await update.message.reply_text("Uso: /aviso tu mensaje")
        return
    msg = " ".join(context.args)
    await context.bot.send_message(chat_id=CANAL_ID, text=f"AVISO - PICKS ELITE\n\n{msg}")
    await update.message.reply_text("Aviso publicado.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not es_admin(update):
        await update.message.reply_text("Sin permiso.")
        return
    total, en_embudo = get_stats()
    await update.message.reply_text(
        f"Estadisticas del Embudo\n\n"
        f"Total usuarios: {total}\n"
        f"En canal gratis: {en_embudo}"
    )

# --- ARRANQUE ---
async def post_init(application: Application):
    await application.bot.delete_webhook(drop_pending_updates=True)
    logger.info("[OK] Webhook borrado. Iniciando polling limpio.")
    await application.bot.set_my_commands([BotCommand("start", "Abrir menu principal")])

def main():
    # Inicializar base de datos
    init_db()

    # Servidor de salud en hilo (Railway)
    threading.Thread(target=run_health_check, daemon=True).start()

    # Construir app
    app = Application.builder().token(TOKEN).post_init(post_init).build()

    # Handlers publicos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id",    get_id))

    # Handlers admin
    app.add_handler(CommandHandler("pick",       publicar_pick))
    app.add_handler(CommandHandler("pickrapido", publicar_pick_rapido))
    app.add_handler(CommandHandler("pronostico", publicar_pick_rapido))
    app.add_handler(CommandHandler("win",        publicar_win))
    app.add_handler(CommandHandler("loss",       publicar_loss))
    app.add_handler(CommandHandler("aviso",      publicar_aviso))
    app.add_handler(CommandHandler("stats",      stats))

    # Callbacks del menu
    app.add_handler(CallbackQueryHandler(cb_canal_gratis, pattern="^canal_gratis$"))
    app.add_handler(CallbackQueryHandler(cb_vip,          pattern="^vip$"))
    app.add_handler(CallbackQueryHandler(cb_resultados,   pattern="^resultados$"))
    app.add_handler(CallbackQueryHandler(cb_about,        pattern="^about$"))
    app.add_handler(CallbackQueryHandler(cb_inicio,       pattern="^inicio$"))

    # Handler universal de texto para capturar cualquier mensaje con /pick o /pickrapido
    async def handle_text_fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message and update.message.text:
            txt = update.message.text.strip().lower()
            logger.info(f"[FALLBACK TEXT] user_id={update.effective_user.id} texto='{txt}'")
            if txt.startswith("/pickrapido") or txt.startswith("pickrapido") or txt.startswith("/pronostico") or txt.startswith("pronostico"):
                await publicar_pick_rapido(update, context)
            elif txt.startswith("/pick") or txt.startswith("pick"):
                await publicar_pick(update, context)

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text_fallback))

    # Error handler
    async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"[ERROR GLOBAL] {context.error}")
        if update and hasattr(update, "message") and update.message:
            try:
                await update.message.reply_text(f"Error interno: {context.error}")
            except Exception:
                pass
    app.add_error_handler(on_error)

    logger.info("[OK] Bot iniciando en modo POLLING...")
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )

if __name__ == "__main__":
    main()
