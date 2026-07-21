import os
import logging
import asyncio
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ——— Módulos propios ———
from config import TOKEN, ADMIN_ID, CANAL_ID, LINK_CANAL_GRATUITO, LINK_CANAL_VIP
from database import Database
from marketing import MarketingFunnel

# =============================================
#   PICKS ELITE BOT — @PicksEliteProBot
#   Versión con embudo de conversión (Fase 1)
# =============================================

# ——— Logging ———
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ——— Inicializar base de datos y módulo de marketing ———
db      = Database()
funnel  = MarketingFunnel(db)
# --- Servidor de salud para Railway (mantiene el servicio activo) ---
def run_health_check_server():
    port = int(os.environ.get("PORT", 8080))
    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
        def log_message(self, format, *args):
            pass
    try:
        HTTPServer(("", port), Handler).serve_forever()
    except Exception as e:
        logger.error(f"[ERROR] Health check: {e}")



# =============================================
#   TEXTOS
# =============================================

BIENVENIDA = """
👑 *¡Bienvenido a Picks Élite!*

⚽ Bienvenido a una comunidad donde el análisis está por encima de la suerte.

Aquí encontrarás:

📊 Pronósticos gratuitos.

📈 Estadísticas transparentes.

💎 Acceso exclusivo al Canal VIP.

🎯 Nuestro objetivo es ayudarte a tomar decisiones más informadas.

👇 Selecciona una opción para comenzar.
"""


# =============================================
#   UTILIDADES
# =============================================

def menu_principal():
    teclado = [
        [InlineKeyboardButton("⚽ Canal Gratuito",     callback_data="canal_gratis")],
        [InlineKeyboardButton("💎 Canal VIP",          callback_data="vip")],
        [InlineKeyboardButton("📊 Resultados",         callback_data="resultados")],
        [InlineKeyboardButton("ℹ️ Sobre Picks Elite",  callback_data="about")],
    ]
    return InlineKeyboardMarkup(teclado)

def boton_volver():
    return [[InlineKeyboardButton("⬅️ Volver al menú", callback_data="inicio")]]

def es_admin(update: Update) -> bool:
    return update.effective_user.id == ADMIN_ID


# =============================================
#   COMANDOS PÚBLICOS
# =============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        BIENVENIDA,
        parse_mode="Markdown",
        reply_markup=menu_principal()
    )

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    nombre  = update.effective_user.first_name
    await update.message.reply_text(
        f"Tu ID de Telegram es:\n\n`{user_id}`\n\nHola {nombre}!",
        parse_mode="Markdown"
    )


# =============================================
#   SECCIONES DEL MENÚ (Callback Queries)
# =============================================

async def canal_gratis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Cuando el usuario pulsa 'Canal Gratuito':
    1. Registra al usuario en la base de datos.
    2. Muestra el mensaje de bienvenida del embudo.
    """
    query = update.callback_query
    await query.answer()

    user = query.from_user
    # Paso 1 — Registrar en el embudo
    funnel.registrar_entrada(user.id, user.username, user.first_name)

    # Paso 2 — Mostrar mensaje de bienvenida
    await funnel.enviar_bienvenida_canal_gratis(context.bot, query)


async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    texto = """
💎 *Canal VIP — Picks Élite Premium*

*¿Qué incluye el VIP?*
✅ 5 a 8 picks premium al día
✅ Análisis H2H detallado
✅ Gestión profesional de bankroll
✅ Casa de apuestas recomendada por pick
✅ Soporte directo con el analista
✅ Alertas de value bets
✅ Acceso al grupo de debate VIP

💰 *Precio: €29 / mes*
_Cancela cuando quieras_

Para suscribirte contáctanos directamente 👇
"""
    teclado = [
        [InlineKeyboardButton("✉️ Contactar para VIP", url=LINK_CANAL_VIP)],
        *boton_volver()
    ]
    await query.edit_message_text(texto, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(teclado))


async def resultados(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    texto = """
📊 *Historial de Resultados — Picks Élite*

🗓 *Julio 2026*
✅ Picks acertados: 0
❌ Picks fallados: 0
📈 Tasa de acierto: —
💰 Unidades: —

_Canal recién lanzado._
_¡Los resultados se actualizarán cada día!_

Síguenos en el canal para ver los picks en tiempo real 👇
"""
    teclado = [
        [InlineKeyboardButton("📢 Ver canal gratuito", url=LINK_CANAL_GRATUITO)],
        *boton_volver()
    ]
    await query.edit_message_text(texto, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(teclado))


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    texto = """
ℹ️ *Sobre Picks Élite*

Canal de pronósticos de fútbol con enfoque *100% estadístico y analítico*.

🎯 *Nuestra filosofía:*
• Transparencia total en resultados
• Análisis basado en datos reales
• Gestión responsable del bankroll
• Apostar con cabeza, no con emoción

📌 Canal gratuito: @PicksElitePro
💎 Canal VIP: Solo para suscriptores
"""
    teclado = [
        [InlineKeyboardButton("📢 Unirse gratis", url=LINK_CANAL_GRATUITO)],
        *boton_volver()
    ]
    await query.edit_message_text(texto, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(teclado))


async def inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.edit_message_text(BIENVENIDA, parse_mode="Markdown", reply_markup=menu_principal())
    except Exception:
        await query.message.reply_text(BIENVENIDA, parse_mode="Markdown", reply_markup=menu_principal())


# =============================================
#   COMANDOS DE PUBLICACIÓN (solo admin)
# =============================================

# ——— /pick partido | apuesta | cuota | liga | hora ———
async def publicar_pick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Respuesta inmediata: confirma que el bot recibio el comando
    user_id = update.effective_user.id if update.effective_user else "?"
    logger.info(f"[PICK] Comando recibido de user_id={user_id}")
    await update.message.reply_text("Recibido. Procesando...")

    if not es_admin(update):
        await update.message.reply_text("Sin permiso. Tu ID: " + str(user_id) + " Admin ID: " + str(ADMIN_ID))
        return

    if not context.args:
        await update.message.reply_text(
            "Formato correcto:\n/pick partido | apuesta | cuota | liga | hora\n\n"
            "Ejemplo:\n/pick Real Madrid vs Barca | Ambos Marcan | 1.80 | LaLiga | 21:00h"
        )
        return

    try:
        partes  = " ".join(context.args).split("|")
        partido = partes[0].strip()
        apuesta = partes[1].strip()
        cuota   = partes[2].strip()
        liga    = partes[3].strip() if len(partes) > 3 else "Futbol"
        hora    = partes[4].strip() if len(partes) > 4 else "Hoy"

        mensaje = (
            f"NUEVA APUESTA GRATUITA\n\n"
            f"Evento: {partido}\n"
            f"Liga: {liga}\n"
            f"Hora: {hora}\n\n"
            f"Pronostico: {apuesta}\n"
            f"Cuota: {cuota}\n"
            f"Stake recomendado: 2/10\n\n"
            f"Realiza tu apuesta ahora antes de que la cuota baje."
        )
        teclado = [
            [InlineKeyboardButton("UNIRSE AL CANAL VIP", url=LINK_CANAL_VIP)],
        ]
        await context.bot.send_message(
            chat_id=CANAL_ID,
            text=mensaje,
            reply_markup=InlineKeyboardMarkup(teclado)
        )
        await update.message.reply_text("Pick publicado en el canal.")
        logger.info(f"[PICK] Publicado: {partido} | {apuesta} | {cuota}")

    except Exception as e:
        error_msg = str(e)
        logger.error(f"[ERROR] /pick fallo: {error_msg}")
        await update.message.reply_text(f"Error al publicar: {error_msg}")


# ——— /win partido | apuesta | cuota ———
async def publicar_win(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not es_admin(update):
        await update.message.reply_text("⛔ No tienes permiso para usar este comando.")
        return

    try:
        partes  = " ".join(context.args).split("|")
        partido = partes[0].strip()
        apuesta = partes[1].strip()
        cuota   = partes[2].strip() if len(partes) > 2 else ""

        cuota_linea = f"📈 *Cuota cobrada:* {cuota}\n" if cuota else ""
        mensaje = (
            f"🟢 *¡¡BOOOOOOOOM VERDE DE PICKS ÉLITE!!* 🟢\n\n"
            f"⚽️ *Evento:* {partido}\n"
            f"🎯 *Pronóstico:* {apuesta} ✅\n"
            f"{cuota_linea}\n"
            f"¡Cobramos otra apuesta gratuita! La racha sigue intacta. "
            f"¡Felicidades a todos los que nos siguieron! 💰🔥\n\n"
            f"🚀 _Si no quieres perderte ningún pick gratuito, activa las notificaciones del canal._"
        )
        teclado = [
            [InlineKeyboardButton("💎 QUIERO SUSCRIBIRME AL VIP", url=LINK_CANAL_VIP)],
        ]
        await context.bot.send_message(
            chat_id=CANAL_ID, text=mensaje, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(teclado)
        )
        await update.message.reply_text("✅ Resultado WIN publicado.")
        logger.info(f"[WIN] Publicado: {partido}")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: `{e}`", parse_mode="Markdown")


# ——— /loss partido | apuesta | cuota ———
async def publicar_loss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not es_admin(update):
        await update.message.reply_text("⛔ No tienes permiso para usar este comando.")
        return

    try:
        partes  = " ".join(context.args).split("|")
        partido = partes[0].strip()
        apuesta = partes[1].strip()
        cuota   = partes[2].strip() if len(partes) > 2 else ""

        cuota_linea = f"📈 *Cuota:* {cuota}\n" if cuota else ""
        mensaje = (
            f"🔴 *ROJO EN ESTE PICK* 🔴\n\n"
            f"⚽️ *Evento:* {partido}\n"
            f"🎯 *Pronóstico:* {apuesta} ❌\n"
            f"{cuota_linea}\n"
            f"Hoy no nos acompañó la suerte en este partido. Transparencia total como siempre. "
            f"Recordad: la clave es la gestión del bankroll a largo plazo.\n\n"
            f"💪 _Seguimos analizando para traeros el próximo verde muy pronto. ¡Cabeza fría!_"
        )
        teclado = [
            [InlineKeyboardButton("📊 VER HISTORIAL COMPLETO", url=LINK_CANAL_GRATUITO)],
            [InlineKeyboardButton("💎 CANAL VIP",              url=LINK_CANAL_VIP)],
        ]
        await context.bot.send_message(
            chat_id=CANAL_ID, text=mensaje, parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(teclado)
        )
        await update.message.reply_text("✅ Resultado LOSS publicado.")
        logger.info(f"[LOSS] Publicado: {partido}")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: `{e}`", parse_mode="Markdown")


# ——— /aviso mensaje ———
async def publicar_aviso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not es_admin(update):
        await update.message.reply_text("⛔ No tienes permiso para usar este comando.")
        return
    if not context.args:
        await update.message.reply_text("Uso: `/aviso tu mensaje aquí`", parse_mode="Markdown")
        return

    mensaje = " ".join(context.args)
    teclado = [[InlineKeyboardButton("📢 Canal Gratuito", url=LINK_CANAL_GRATUITO)]]
    await context.bot.send_message(
        chat_id=CANAL_ID,
        text=f"📢 *AVISO — PICKS ÉLITE*\n\n{mensaje}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(teclado)
    )
    await update.message.reply_text("✅ Aviso publicado en el canal.")


# ——— /stats (solo admin) — Ver estadísticas del embudo ———
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not es_admin(update):
        await update.message.reply_text("⛔ No tienes permiso para usar este comando.")
        return

    import sqlite3
    from config import DB_PATH
    with sqlite3.connect(DB_PATH) as conn:
        total       = conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
        en_embudo   = conn.execute("SELECT COUNT(*) FROM usuarios WHERE estado_embudo = 'canal_gratis'").fetchone()[0]
        enviados_24 = conn.execute("SELECT COUNT(*) FROM usuarios WHERE enviado_24h = 1").fetchone()[0]
        enviados_72 = conn.execute("SELECT COUNT(*) FROM usuarios WHERE enviado_72h = 1").fetchone()[0]
        enviados_7d = conn.execute("SELECT COUNT(*) FROM usuarios WHERE enviado_7d  = 1").fetchone()[0]

    await update.message.reply_text(
        f"📊 *Estadísticas del Embudo*\n\n"
        f"👤 Total usuarios registrados: `{total}`\n"
        f"⚽ En embudo (canal gratis): `{en_embudo}`\n\n"
        f"📩 Follow-ups enviados:\n"
        f"  • 24h: `{enviados_24}`\n"
        f"  • 72h: `{enviados_72}`\n"
        f"  • 7 días: `{enviados_7d}`",
        parse_mode="Markdown"
    )


# =============================================
#   ARRANQUE DEL BOT
# =============================================

async def post_init(application: Application):
    """Configuración que se ejecuta una sola vez al iniciar el bot."""
    # Solo mostramos /start en el menú de comandos (los de admin son ocultos)
    await application.bot.set_my_commands([
        BotCommand("start", "Abrir menú principal"),
    ])
    # Arrancar el scheduler de follow-ups en segundo plano
    asyncio.create_task(funnel.iniciar_scheduler(application.bot))
    logger.info("[OK] Scheduler de follow-ups iniciado en segundo plano.")


def main():
    # Servidor de salud en hilo secundario (Railway necesita respuesta HTTP)
    threading.Thread(target=run_health_check_server, daemon=True).start()

    app = (
        Application.builder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )

    # ——— Comandos públicos ———
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id",    get_id))

    # ——— Comandos de admin ———
    app.add_handler(CommandHandler("pick",  publicar_pick))
    app.add_handler(CommandHandler("win",   publicar_win))
    app.add_handler(CommandHandler("loss",  publicar_loss))
    app.add_handler(CommandHandler("aviso", publicar_aviso))
    app.add_handler(CommandHandler("stats", stats))

    # ——— Botones del menú ———
    app.add_handler(CallbackQueryHandler(canal_gratis, pattern="^canal_gratis$"))
    app.add_handler(CallbackQueryHandler(vip,          pattern="^vip$"))
    app.add_handler(CallbackQueryHandler(resultados,   pattern="^resultados$"))
    app.add_handler(CallbackQueryHandler(about,        pattern="^about$"))
    app.add_handler(CallbackQueryHandler(inicio,       pattern="^inicio$"))

    logger.info("[OK] Picks Elite Bot arrancado correctamente...")
    logger.info("[OK] @PicksEliteProBot esta activo - esperando mensajes...")

    # Manejador de errores global
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"[ERROR GLOBAL] {context.error}")
        if update and hasattr(update, 'message') and update.message:
            try:
                await update.message.reply_text(f"Error interno: {context.error}")
            except Exception:
                pass
    app.add_error_handler(error_handler)

    # =============================================
    #   MODO DE ARRANQUE: POLLING
    #   Funciona correctamente porque solo hay UNA
    #   instancia corriendo (en Railway).
    #   El error "Conflict" ocurria porque antes
    #   corrias el bot tambien en tu PC al mismo tiempo.
    # =============================================
    logger.info("[OK] Iniciando en modo POLLING...")
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
