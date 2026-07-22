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
    cuota_txt = f" | Cuota {cuota} 💰" if cuota else ""
    return (
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏆✨ *¡¡ V E R D E !!* ✨🏆\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥\n\n"
        f"⚽ *{partido}*\n\n"
        f"✅ *{apuesta}*{cuota_txt} — *GANADO*\n\n"
        f"🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥\n\n"
        f"💚 *Otra apuesta, otro verde.*\n"
        f"📈 Esto es análisis, no suerte.\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"💎 *Picks Élite — Apuesta con cabeza*"
    )

def format_doble_win(partido: str, apuesta1: str, apuesta2: str, cuota1: str = "", cuota2: str = "") -> str:
    c1 = f" | Cuota {cuota1} 💰" if cuota1 else ""
    c2 = f" | Cuota {cuota2} 💰" if cuota2 else ""
    return (
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🏆🔥 *¡¡ D O S   V E R D E S !!* 🔥🏆\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💥💥💥💥💥💥💥💥💥💥💥💥\n\n"
        f"⚽ *{partido}*\n\n"
        f"✅ *{apuesta1}*{c1} — *GANADO*\n"
        f"✅ *{apuesta2}*{c2} — *GANADO*\n\n"
        f"💥💥💥💥💥💥💥💥💥💥💥💥\n\n"
        f"💚 *Dos de dos. Sin fallos.*\n"
        f"📈 Puro análisis. Pura estadística.\n"
        f"🎯 Racha activa. Confianza máxima.\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"💎 *¿Quieres los picks VIP con cuotas más altas?*\n"
        f"👇 Accede al canal premium ahora mismo\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🍀 *Picks Élite — Apuesta con cabeza*"
    )

def format_resultado(partido: str, resultado: str, pick1: str, pick2: str = "", detalle: str = "") -> str:
    pick2_txt = f"\n✅ *{pick2}*" if pick2 else ""
    detalle_txt = f"\n\n_{detalle}_" if detalle else ""
    return (
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 *ANÁLISIS POST-PARTIDO*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⚽ *{partido}*\n"
        f"🏁 Resultado final: *{resultado}*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 *NUESTROS PICKS*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✅ *{pick1}*{pick2_txt}\n"
        f"{detalle_txt}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📈 Esto es análisis, no suerte.\n"
        f"💎 *Picks Élite — Apuesta con cabeza* 🍀"
    )

def format_loss(partido: str, apuesta: str) -> str:
    return (
        f"🔴 *ROJO EN ESTE PICK* 🔴\n\n"
        f"⚽️ *Evento:* {partido}\n"
        f"🎯 *Pronóstico:* {apuesta} ❌\n\n"
        f"Transparencia total como siempre. Recordad que la clave es la gestión del bankroll.\n\n"
        f"💪 _Seguimos analizando para traeros el próximo verde pronto._"
    )
