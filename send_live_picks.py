import sys
import io
import urllib.request
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

token = "8915840915:AAFWX7lh3wxO3QKWutoCMdYB7l-TcJ5aQJQ"
canal_gratis = "@PicksElitePro"
canal_vip    = -1004381972016

img_gratis = r"C:\Users\Asus\Desktop\Archivo\live_free_banner.jpg"
img_vip    = r"C:\Users\Asus\Desktop\Archivo\live_vip_banner.jpg"

caption_gratis = (
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "🚨🔥  ENTRAMOS EN DIRECTO  🔥🚨\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "⚽ *Boca Juniors vs CA Talleres de Cordoba*\n"
    "🏆 Argentina - Primera A | 🔴 *EN VIVO*\n\n"
    "🎯 *Pronostico:* Mas de 0.5 goles (1a Parte)\n"
    "📈 *Cuota:* 1.60\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "⚡ *ESTRATEGIA 1500*\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "📌 Hemos detectado alta presion ofensiva en estos primeros minutos.\n\n"
    "🔒 _La explicacion completa de la Estrategia 1500 la compartiremos de forma exclusiva en el canal VIP._\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "💎 Picks Elite  |  Apuesta con cabeza 🍀"
)

keyboard_gratis = json.dumps({
    "inline_keyboard": [[
        {"text": "👑 ENTRAR AL CANAL VIP", "url": "https://t.me/+ldrgDvLiC5NhOTRk"}
    ]]
})

caption_vip = (
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "👑💎  LIVE VIP — ESTRATEGIA 1500  💎👑\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "⚽ *Boca Juniors vs CA Talleres de Cordoba*\n"
    "🏆 Argentina - Primera A | 🔴 *EN VIVO*\n\n"
    "🎯 *Pronostico:* Mas de 0.5 goles (1a Parte)\n"
    "📈 *Cuota:* 1.60\n"
    "💵 *Stake recomendado:* 3/10\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "⚡ *ESTRATEGIA 1500 EN ACCION*\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "📌 Filtro algoritmico activado: Ritmo alto de juego + tiros a puerta acumulados en los primeros minutos.\n\n"
    "🎯 Entramos con fuerza antes del descanso.\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "🍀 Picks Elite VIP  |  Apuesta con cabeza"
)

def send_photo(chat_id, img_path, caption, reply_markup=None):
    boundary = "FormBoundLiveSend"
    with open(img_path, "rb") as f:
        img_data = f.read()

    def field(n, v):
        return (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{n}\"\r\n\r\n{v}\r\n").encode("utf-8")

    photo_header = (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"photo\"; filename=\"banner.jpg\"\r\n"
        f"Content-Type: image/jpeg\r\n\r\n"
    ).encode("utf-8")

    body = field("chat_id", str(chat_id)) + field("caption", caption) + field("parse_mode", "Markdown")
    if reply_markup:
        body += field("reply_markup", reply_markup)
    body += photo_header + img_data + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendPhoto",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )

    try:
        res = urllib.request.urlopen(req)
        data = json.loads(res.read().decode("utf-8"))
        if data.get("ok"):
            print(f"✅ Publicado en {chat_id} | message_id: {data['result']['message_id']}")
        else:
            print(f"❌ Error en {chat_id}:", data)
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error en {chat_id}:", e.read().decode("utf-8"))

print("🚀 Publicando Pick en Directo...")
send_photo(canal_gratis, img_gratis, caption_gratis, keyboard_gratis)
send_photo(canal_vip, img_vip, caption_vip)
