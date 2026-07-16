from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# =============================================
#   PICKS ELITE BOT - @PicksEliteProBot
# =============================================

TOKEN       = "8915840915:AAEN1o7abYvMw6r11XEbY7eFxmTw-ccX3Q4"
CANAL_ID    = "@PicksElitePro"
CANAL_GRATIS = "https://t.me/PicksElitePro"
ADMIN_ID    = 8516113803   # Solo el admin puede publicar picks

# ——— TEXTO BIENVENIDA ———
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

# ——— MENÚ PRINCIPAL (reutilizable) ———
def menu_principal():
    teclado = [
        [InlineKeyboardButton("⚽ Canal Gratuito", callback_data="canal_gratis")],
        [InlineKeyboardButton("💎 Canal VIP",      callback_data="vip")],
        [InlineKeyboardButton("📊 Resultados",     callback_data="resultados")],
        [InlineKeyboardButton("ℹ️ Sobre Picks Elite", callback_data="about")],
    ]
    return InlineKeyboardMarkup(teclado)

# ——— BOTÓN VOLVER (reutilizable) ———
def boton_volver():
    return [[InlineKeyboardButton("⬅️ Volver al menú", callback_data="inicio")]]

# ——— COMANDO /start ———
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        BIENVENIDA,
        parse_mode="Markdown",
        reply_markup=menu_principal()
    )

# ——— SECCIÓN CANAL GRATUITO ———
async def canal_gratis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    texto = """
⚽ *Canal Gratuito — Picks Élite*

Publicamos picks gratuitos cada día con análisis estadístico real.

✅ Picks diarios con cuota incluida
📊 Historial 100% transparente
🎯 Análisis antes de cada partido
📈 Actualizado en tiempo real

👇 Entra ahora al canal:
"""
    teclado = [
        [InlineKeyboardButton("📢 Entrar al canal", url=CANAL_GRATIS)],
        *boton_volver()
    ]
    await query.edit_message_text(
        texto,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(teclado)
    )

# ——— SECCIÓN VIP ———
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
        [InlineKeyboardButton("✉️ Contactar para VIP", url=CANAL_GRATIS)],
        *boton_volver()
    ]
    await query.edit_message_text(
        texto,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(teclado)
    )

# ——— SECCIÓN RESULTADOS ———
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
        [InlineKeyboardButton("📢 Ver canal gratuito", url=CANAL_GRATIS)],
        *boton_volver()
    ]
    await query.edit_message_text(
        texto,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(teclado)
    )

# ——— SECCIÓN ABOUT ———
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

⚠️ _Apostar implica riesgos. Solo mayores de 18 años._
"""
    teclado = [
        [InlineKeyboardButton("📢 Unirse gratis", url=CANAL_GRATIS)],
        *boton_volver()
    ]
    await query.edit_message_text(
        texto,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(teclado)
    )

# ——— VOLVER AL MENÚ PRINCIPAL ———
async def inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        await query.edit_message_text(
            BIENVENIDA,
            parse_mode="Markdown",
            reply_markup=menu_principal()
        )
    except Exception:
        await query.message.reply_text(
            BIENVENIDA,
            parse_mode="Markdown",
            reply_markup=menu_principal()
        )

# =============================================
#   COMANDOS DE PUBLICACIÓN (solo admin)
# =============================================

def es_admin(update: Update) -> bool:
    return update.effective_user.id == ADMIN_ID

# ——— /pick partido | apuesta | cuota | liga | hora ———
async def publicar_pick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not es_admin(update):
        await update.message.reply_text("No tienes permiso para usar este comando.")
        return

    try:
        args = " ".join(context.args).split("|")
        partido  = args[0].strip()
        apuesta  = args[1].strip()
        cuota    = args[2].strip()
        liga     = args[3].strip() if len(args) > 3 else "Fútbol"
        hora     = args[4].strip() if len(args) > 4 else "Hoy"

        mensaje = f"""
🔥 *PICK GRATUITO — PICKS ÉLITE* 🔥

⚽ *{partido}*
🏆 {liga}
⏰ {hora}

━━━━━━━━━━━━━━━━━━━
📌 *Apuesta:* {apuesta}
📊 *Cuota:* {cuota}
💰 *Stake:* 2/10 unidades
━━━━━━━━━━━━━━━━━━━

🎯 Selección validada por nuestro equipo analítico.

⚠️ _Apostar implica riesgos. Solo mayores de 18 años._
"""
        teclado = [
            [InlineKeyboardButton("💎 Acceder al Canal VIP", url="https://t.me/PicksEliteProBot")],
            [InlineKeyboardButton("📢 Canal Gratuito", url=CANAL_GRATIS)],
        ]
        await context.bot.send_message(
            chat_id=CANAL_ID,
            text=mensaje,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(teclado)
        )
        await update.message.reply_text("✅ Pick publicado en el canal!")

    except Exception as e:
        await update.message.reply_text(
            f"Error al publicar. Usa el formato correcto:\n\n"
            f"`/pick partido | apuesta | cuota | liga | hora`\n\n"
            f"Ejemplo:\n`/pick Real Madrid vs Barcelona | +2.5 goles | 1.85 | LaLiga | 20:00h`",
            parse_mode="Markdown"
        )

# ——— /win partido | apuesta | cuota ———
async def publicar_win(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not es_admin(update):
        await update.message.reply_text("No tienes permiso para usar este comando.")
        return

    try:
        args = " ".join(context.args).split("|")
        partido = args[0].strip()
        apuesta = args[1].strip()
        cuota   = args[2].strip() if len(args) > 2 else ""

        mensaje = f"""
✅ *RESULTADO: VERDE* 🟢

⚽ *{partido}*
📌 {apuesta} ✅
{f'📊 Cuota: {cuota}' if cuota else ''}

💰 *¡Pick ganador para Picks Élite!*
📈 Seguimos sumando unidades.

👇 No te pierdas el próximo pick:
"""
        teclado = [
            [InlineKeyboardButton("🔔 Activar notificaciones", url=CANAL_GRATIS)],
            [InlineKeyboardButton("💎 Canal VIP", url="https://t.me/PicksEliteProBot")],
        ]
        await context.bot.send_message(
            chat_id=CANAL_ID,
            text=mensaje,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(teclado)
        )
        await update.message.reply_text("✅ Resultado WIN publicado!")

    except Exception as e:
        await update.message.reply_text(
            "Formato: `/win partido | apuesta | cuota`",
            parse_mode="Markdown"
        )

# ——— /loss partido | apuesta | cuota ———
async def publicar_loss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not es_admin(update):
        await update.message.reply_text("No tienes permiso para usar este comando.")
        return

    try:
        args = " ".join(context.args).split("|")
        partido = args[0].strip()
        apuesta = args[1].strip()
        cuota   = args[2].strip() if len(args) > 2 else ""

        mensaje = f"""
❌ *RESULTADO: ROJO* 🔴

⚽ *{partido}*
📌 {apuesta} ❌
{f'📊 Cuota: {cuota}' if cuota else ''}

📊 Transparencia total. Esto también pasa.
💪 *La racha positiva continúa. Seguimos.*

Gestiona tu bankroll con responsabilidad 👇
"""
        teclado = [
            [InlineKeyboardButton("📊 Ver historial completo", url=CANAL_GRATIS)],
            [InlineKeyboardButton("💎 Canal VIP", url="https://t.me/PicksEliteProBot")],
        ]
        await context.bot.send_message(
            chat_id=CANAL_ID,
            text=mensaje,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(teclado)
        )
        await update.message.reply_text("✅ Resultado LOSS publicado!")

    except Exception as e:
        await update.message.reply_text(
            "Formato: `/loss partido | apuesta | cuota`",
            parse_mode="Markdown"
        )

# ——— /aviso mensaje ———
async def publicar_aviso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not es_admin(update):
        await update.message.reply_text("No tienes permiso para usar este comando.")
        return

    if not context.args:
        await update.message.reply_text("Uso: `/aviso tu mensaje aquí`", parse_mode="Markdown")
        return

    mensaje = " ".join(context.args)
    teclado = [
        [InlineKeyboardButton("📢 Canal Gratuito", url=CANAL_GRATIS)],
    ]
    await context.bot.send_message(
        chat_id=CANAL_ID,
        text=f"📢 *AVISO — PICKS ÉLITE*\n\n{mensaje}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(teclado)
    )
    await update.message.reply_text("✅ Aviso publicado en el canal!")

# ——— /id (obtener tu ID de Telegram) ———
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    nombre  = update.effective_user.first_name
    await update.message.reply_text(
        f"Tu ID de Telegram es:\n\n`{user_id}`\n\nHola {nombre}!",
        parse_mode="Markdown"
    )

# ——— CONFIGURACIÓN INICIAL DEL BOT ———
async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "Abrir menu principal"),
        BotCommand("pick",  "Publicar pick en el canal (admin)"),
        BotCommand("win",   "Publicar resultado ganado (admin)"),
        BotCommand("loss",  "Publicar resultado perdido (admin)"),
        BotCommand("aviso", "Publicar aviso en el canal (admin)"),
    ])

# ——— INICIAR BOT ———
def main():
    app = Application.builder().token(TOKEN).post_init(post_init).build()

    # Comandos públicos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id",    get_id))

    # Comandos de admin
    app.add_handler(CommandHandler("pick",  publicar_pick))
    app.add_handler(CommandHandler("win",   publicar_win))
    app.add_handler(CommandHandler("loss",  publicar_loss))
    app.add_handler(CommandHandler("aviso", publicar_aviso))

    # Botones — patrones exactos
    app.add_handler(CallbackQueryHandler(canal_gratis, pattern="^canal_gratis$"))
    app.add_handler(CallbackQueryHandler(vip,          pattern="^vip$"))
    app.add_handler(CallbackQueryHandler(resultados,   pattern="^resultados$"))
    app.add_handler(CallbackQueryHandler(about,        pattern="^about$"))
    app.add_handler(CallbackQueryHandler(inicio,       pattern="^inicio$"))

    print("[OK] Picks Elite Bot arrancado correctamente...")
    print("[OK] @PicksEliteProBot esta activo - esperando mensajes...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
