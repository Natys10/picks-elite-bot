# =============================================
#   MOTOR DE PLANTILLAS VISUALES PARA PICKS
# =============================================

def format_pronostico_rapido(partido: str, apuesta: str, cuota: str, motivo: str = "") -> str:
    motivo_txt = f"\nMotivo: {motivo}\n" if motivo else ""
    return (
        f"⚡️ *PRONÓSTICO RÁPIDO*\n\n"
        f"*{partido}*\n"
        f"➡️ {apuesta}\n"
        f"➡️ Cuota: {cuota}\n"
        f"{motivo_txt}\n"
        f"Suerte 🍀\n"
        f"Apuesta con cabeza"
    )

def format_directo(partido: str, apuesta: str, periodo: str = "Primera Parte", cuota: str = "") -> str:
    return (
        f"🚨 *ENTRAMOS EN DIRECTO* 🚨\n\n"
        f"⚽ {partido}\n\n"
        f"🎯 {apuesta}\n"
        f"⏱️ {periodo}\n\n"
        f"📈 Cuota {cuota}"
    )

def format_pick_elite(partido: str, apuesta: str, cuota: str, liga: str = "Fútbol", hora: str = "Hoy", stake: str = "2/10") -> str:
    return (
        f"🔥 *NUEVA APUESTA GRATUITA* 🔥\n\n"
        f"⚽️ *Evento:* {partido}\n"
        f"🏆 *Liga:* {liga}\n"
        f"⏰ *Hora:* {hora}\n\n"
        f"🎯 *Pronóstico:* {apuesta}\n"
        f"📈 *Cuota:* {cuota}\n"
        f"💰 *Stake recomendado:* {stake}\n\n"
        f"⚡️ _Realiza tu apuesta ahora antes de que la cuota baje. ¡Vamos con todo!_"
    )

def format_win(partido: str, apuesta: str, cuota: str = "") -> str:
    cuota_txt = f"\n📈 *Cuota cobrada:* {cuota}" if cuota else ""
    return (
        f"🟢 *¡¡BOOOOOOOOM VERDE DE PICKS ÉLITE!!* 🟢\n\n"
        f"⚽️ *Evento:* {partido}\n"
        f"🎯 *Pronóstico:* {apuesta} ✅{cuota_txt}\n\n"
        f"¡Cobramos otra apuesta gratuita! La racha sigue intacta. 💰🔥\n\n"
        f"🚀 _Activa las notificaciones del canal para no perderte el próximo._"
    )

def format_loss(partido: str, apuesta: str) -> str:
    return (
        f"🔴 *ROJO EN ESTE PICK* 🔴\n\n"
        f"⚽️ *Evento:* {partido}\n"
        f"🎯 *Pronóstico:* {apuesta} ❌\n\n"
        f"Transparencia total como siempre. Recordad que la clave es la gestión del bankroll.\n\n"
        f"💪 _Seguimos analizando para traeros el próximo verde pronto._"
    )
