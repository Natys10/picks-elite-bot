from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# =============================================
#   PICKS ELITE BOT - @PicksEliteProBot
# =============================================

TOKEN = "8915840915:AAEN1o7abYvMw6r11XEbY7eFxmTw-ccX3Q4"
CANAL_GRATIS = "https://t.me/PicksElitePro"

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
        [InlineKeyboardButton("⚽ Canal Gratuito", url=CANAL_GRATIS)],
        [InlineKeyboardButton("💎 Canal VIP", callback_data="vip")],
        [InlineKeyboardButton("📊 Resultados", callback_data="resultados")],
        [InlineKeyboardButton("ℹ️ Sobre Picks Elite", callback_data="about")],
    ]
    return InlineKeyboardMarkup(teclado)

# ——— COMANDO /start ———
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        BIENVENIDA,
        parse_mode="Markdown",
        reply_markup=menu_principal()
    )

# ——— BOTÓN VIP ———
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
        [InlineKeyboardButton("⬅️ Volver al menú", callback_data="inicio")],
    ]
    await query.edit_message_text(
        texto,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(teclado)
    )

# ——— BOTÓN RESULTADOS ———
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
        [InlineKeyboardButton("⬅️ Volver al menú", callback_data="inicio")],
    ]
    await query.edit_message_text(
        texto,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(teclado)
    )

# ——— BOTÓN ABOUT ———
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
        [InlineKeyboardButton("⬅️ Volver al menú", callback_data="inicio")],
    ]
    await query.edit_message_text(
        texto,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(teclado)
    )

# ——— VOLVER AL MENÚ PRINCIPAL (reutiliza menu_principal y BIENVENIDA) ———
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
        # Si no se puede editar, envía un mensaje nuevo
        await query.message.reply_text(
            BIENVENIDA,
            parse_mode="Markdown",
            reply_markup=menu_principal()
        )

# ——— INICIAR BOT ———
def main():
    app = Application.builder().token(TOKEN).build()

    # Comando
    app.add_handler(CommandHandler("start", start))

    # Botones — patrones exactos para evitar conflictos
    app.add_handler(CallbackQueryHandler(vip,        pattern="^vip$"))
    app.add_handler(CallbackQueryHandler(resultados, pattern="^resultados$"))
    app.add_handler(CallbackQueryHandler(about,      pattern="^about$"))
    app.add_handler(CallbackQueryHandler(inicio,     pattern="^inicio$"))

    print("[OK] Picks Elite Bot arrancado correctamente...")
    print("[OK] @PicksEliteProBot esta activo - esperando mensajes...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
