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
ESPERANDO_CUSTOM    = 9
ESPERANDO_DESTINO_CUSTOM = 10

# Banners por tipo de publicación
BANNERS = {
    "win":       os.path.join(os.path.dirname(__file__), "win_banner.jpg"),
    "pick":      os.path.join(os.path.dirname(__file__), "pick_banner.jpg"),
    "directo":   os.path.join(os.path.dirname(__file__), "live_free_banner.jpg"),
    "vip_pick":  os.path.join(os.path.dirname(__file__), "vip_pick_banner.jpg"),
    "vip_live":  os.path.join(os.path.dirname(__file__), "live_vip_banner.jpg"),
    "loss":      os.path.join(os.path.dirname(__file__), "win_banner.jpg"),
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
        [InlineKeyboardButton("📢 Acceder al Canal Gratuito", url=get_link_gratis())],
        [InlineKeyboardButton("💎 Información VIP", callback_data="vip")],
        [InlineKeyboardButton("📊 Estadísticas", callback_data="resultados"), InlineKeyboardButton("ℹ️ Info", callback_data="about")]
    ])

def btn_volver_menu():
    return [[InlineKeyboardButton("⬅️ Volver al menú", callback_data="inicio")]]

def btn_volver_admin():
    return [[InlineKeyboardButton("⬅️ Volver al panel", callback_data="admin_menu")]]

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
        try:
            db.registrar_usuario(user.id, user.username, user.first_name)
            db.log_evento(user.id, "start")
        except Exception as e:
            logger.error(f"[START DB ERROR] {e}")

    texto = db.get_config("start_text", 
        "👑 *Bienvenido a Picks Élite*\n\n"
        "Selecciona una opción del menú para comenzar:"
    )
    
    await update.message.reply_text(
        texto, parse_mode="Markdown", reply_markup=menu_principal()
    )

async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Aprueba automáticamente las solicitudes de unión al canal y envía mensaje de bienvenida"""
    request = update.chat_join_request
    try:
        await request.approve()
        
        # Registrar al usuario
        user = request.from_user
        db.registrar_usuario(user.id, user.username, user.first_name)
        
        # Enviar mensaje automático por privado (como en la captura 3)
        msg_bienvenida = (
            "✅ *¡Solicitud Aprobada!*\n\n"
            "Ya estás dentro de nuestro **Canal Gratuito**.\n"
            "Prepárate para recibir los mejores picks estadísticos del mercado.\n\n"
            "¿Quieres llevar tu bankroll al siguiente nivel?\n"
            "Únete a nuestro **Canal VIP** hoy mismo."
        )
        teclado = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 Información VIP", callback_data="vip")]
        ])
        
        await context.bot.send_message(
            chat_id=user.id,
            text=msg_bienvenida,
            parse_mode="Markdown",
            reply_markup=teclado
        )
        
    except Exception as e:
        logger.error(f"Error en join request: {e}")

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(f"Tu ID de Telegram es: `{uid}`", parse_mode="Markdown")

# =============================================
#   CALLBACKS MENÚ PÚBLICO
# =============================================
async def cb_menu_inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    texto = "👑 *Bienvenido a Picks Élite*\n\nSelecciona una opción del menú:"
    await query.edit_message_text(texto, parse_mode="Markdown", reply_markup=menu_principal())
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
    link_admin = db.get_config("link_admin", "https://t.me/TuUsuarioAqui")
    teclado = [
        [InlineKeyboardButton("💬 Contactar para Pago y Acceso", url=link_admin)],
        *btn_volver_menu(),
    ]
    await query.edit_message_text(texto, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(teclado))

async def cb_resultados(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    texto = (
        "📊 *Nuestros Resultados*\n\n"
        "Mantenemos un historial 100% transparente en nuestro canal público.\n"
        "Únete y comprueba los últimos resultados."
    )
    teclado = [
        [InlineKeyboardButton("📢 Ver en el Canal Gratuito", url=get_link_gratis())],
        *btn_volver_menu()
    ]
    await query.edit_message_text(texto, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(teclado))

async def cb_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    texto = (
        "ℹ️ *Sobre Picks Élite*\n\n"
        "Somos un equipo de analistas enfocados en mercados líquidos y líneas de valor.\n"
        "Trabajamos con estadística avanzada para rentabilizar a largo plazo."
    )
    teclado = btn_volver_menu()
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
        [InlineKeyboardButton("📝 Publicación Libre", callback_data="pub_custom")],
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
    "pub_custom": (
        ESPERANDO_CUSTOM,
        "📝 *PUBLICACIÓN LIBRE*\n\n"
        "Envía o reenvía el mensaje que quieres publicar.\n"
        "Puede ser un texto, foto, vídeo, GIF o audio.\n\n"
        "_El bot te preguntará a qué canal enviarlo después._"
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
#   MANEJADOR DE ENTRADA (publicaciones y contenido libre)
# =============================================
async def handle_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    uid = update.effective_user.id
    if not admin.is_admin(uid): return

    estado = context.user_data.get("pub_estado")
    
    # Manejar texto si es texto o tiene caption
    text = update.message.text or update.message.caption or ""
    text = text.strip()

    # Cancelar (si es comando de texto)
    if text.lower() in ["/cancelar", "cancelar"]:
        context.user_data.pop("pub_estado", None)
        context.user_data.pop("pub_tipo", None)
        context.user_data.pop("custom_msg_id", None)
        await update.message.reply_text("❌ Operación cancelada.", reply_markup=get_panel_admin_markup())
        return

    # NUEVO ESTADO: ESPERANDO_CUSTOM
    if estado == ESPERANDO_CUSTOM:
        context.user_data["custom_msg_id"] = update.message.message_id
        context.user_data["pub_estado"] = ESPERANDO_DESTINO_CUSTOM
        teclado = [
            [InlineKeyboardButton("📢 Canal Gratuito", callback_data="dest_gratis")],
            [InlineKeyboardButton("💎 Canal VIP", callback_data="dest_vip")],
            [InlineKeyboardButton("🔥 AMBOS Canales", callback_data="dest_ambos")],
            [InlineKeyboardButton("❌ Cancelar", callback_data="admin_publicar")]
        ]
        await update.message.reply_text(
            "✅ Contenido recibido.\n\n¿Dónde quieres publicar este mensaje?",
            reply_markup=InlineKeyboardMarkup(teclado)
        )
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

async def cb_pub_destino(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not admin.is_admin(query.from_user.id): return
    
    estado = context.user_data.get("pub_estado")
    if estado != ESPERANDO_DESTINO_CUSTOM:
        return
        
    destino = query.data
    msg_id = context.user_data.get("custom_msg_id")
    
    if not msg_id:
        await query.edit_message_text("❌ Error: No se encontró el mensaje a publicar.", reply_markup=get_panel_admin_markup())
        return

    chat_origen = query.message.chat_id
    
    try:
        if destino == "dest_gratis":
            await context.bot.copy_message(chat_id=CANAL_ID, from_chat_id=chat_origen, message_id=msg_id)
            await query.edit_message_text("✅ Publicado en el Canal Gratuito exitosamente.", reply_markup=get_panel_admin_markup())
        elif destino == "dest_vip":
            await context.bot.copy_message(chat_id=CANAL_VIP_ID, from_chat_id=chat_origen, message_id=msg_id)
            await query.edit_message_text("✅ Publicado en el Canal VIP exitosamente.", reply_markup=get_panel_admin_markup())
        elif destino == "dest_ambos":
            await context.bot.copy_message(chat_id=CANAL_ID, from_chat_id=chat_origen, message_id=msg_id)
            await context.bot.copy_message(chat_id=CANAL_VIP_ID, from_chat_id=chat_origen, message_id=msg_id)
            await query.edit_message_text("✅ Publicado en AMBOS canales exitosamente.", reply_markup=get_panel_admin_markup())
            
        context.user_data.pop("pub_estado", None)
        context.user_data.pop("custom_msg_id", None)
    except Exception as e:
        await query.edit_message_text(f"❌ Error al publicar: `{e}`", parse_mode="Markdown", reply_markup=get_panel_admin_markup())

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
    elif tipo == "admin":
        db.set_config("link_admin", url)
        await update.message.reply_text(f"✅ Link de Administrador actualizado: `{url}`", parse_mode="Markdown")
    else:
        await update.message.reply_text("Tipo inválido. Usa `gratis`, `vip` o `admin`.", parse_mode="Markdown")

# =============================================
#   ARRANQUE
# =============================================
async def post_init(application: Application):
    await application.bot.delete_webhook(drop_pending_updates=True)
    # Limpiar comandos viejos cacheados antes de registrar los nuevos
    await application.bot.delete_my_commands()
    await application.bot.set_my_commands([
        BotCommand("start",  "Abrir menú principal"),
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
    from telegram.ext import ChatJoinRequestHandler
    app.add_handler(ChatJoinRequestHandler(handle_join_request))
    app.add_handler(CallbackQueryHandler(cb_vip,        pattern="^vip$"))
    app.add_handler(CallbackQueryHandler(cb_resultados, pattern="^resultados$"))
    app.add_handler(CallbackQueryHandler(cb_about,      pattern="^about$"))
    app.add_handler(CallbackQueryHandler(cb_inicio,     pattern="^inicio$"))

    # Admin comandos directos
    app.add_handler(CommandHandler("admin",  cmd_admin))
    app.add_handler(CommandHandler("stats",  cmd_stats))
    app.add_handler(CommandHandler("setlink", cmd_setlink))

    # Callbacks panel admin
    app.add_handler(CallbackQueryHandler(cb_admin_menu,      pattern="^admin_menu$"))
    app.add_handler(CallbackQueryHandler(cb_admin_stats,     pattern="^admin_stats$"))
    app.add_handler(CallbackQueryHandler(cb_admin_publicar,  pattern="^admin_publicar$"))
    app.add_handler(CallbackQueryHandler(cb_admin_edit_start,pattern="^admin_edit_start$"))
    app.add_handler(CallbackQueryHandler(cb_admin_broadcast, pattern="^admin_broadcast_info$"))
    app.add_handler(CallbackQueryHandler(cb_admin_edit_links,pattern="^admin_edit_links$"))

    # Callbacks submenú publicación
    app.add_handler(CallbackQueryHandler(cb_pub_tipo, pattern="^pub_"))
    app.add_handler(CallbackQueryHandler(cb_pub_destino, pattern="^dest_"))

    # Manejador general (texto, media, etc.) para publicaciones libres y plantillas
    app.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), handle_admin_input))

    logger.info("[OK] Picks Elite Platform arrancada en modo POLLING...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
