import sys, io, urllib.request, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

token  = "8915840915:AAFWX7lh3wxO3QKWutoCMdYB7l-TcJ5aQJQ"
canal  = -1004381972016   # Canal VIP privado
img    = r"C:\Users\Asus\Desktop\Archivo\vip_pick_banner.jpg"

caption = (
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "👑💎  VIP PICK  |  COMBINADA x2  💎👑\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"

    "🇦🇷 ARGENTINA - PRIMERA C\n\n"

    "Pick 1\n"
    "⚽ Satsaid (F) vs Ferro Carril Oeste (F)\n"
    "🎯 Ambos equipos marcan: SI\n"
    "📈 Cuota: 2.00\n"
    "🕐 Hora: 17:00h\n\n"

    "Pick 2\n"
    "⚽ Boca Juniors (F) vs CA Talleres (F)\n"
    "🎯 Mas de 1.5 goles (Boca Juniors)\n"
    "📈 Cuota: 2.35\n"
    "🕐 Hora: 16:00h\n\n"

    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "🔗 COMBINADA VIP\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "💰 Cuota total: 4.70\n"
    "💵 Stake recomendado: 3/10\n\n"
    "⚠️ Gestiona siempre tu bankroll.\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "💎 Picks Elite VIP  |  Apuesta con cabeza 🍀"
)

boundary = "FormBoundVIPPICK"
with open(img, "rb") as f:
    img_data = f.read()

def field(n, v):
    return (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{n}\"\r\n\r\n{v}\r\n").encode("utf-8")

photo_header = (
    f"--{boundary}\r\n"
    f"Content-Disposition: form-data; name=\"photo\"; filename=\"vip_pick_banner.jpg\"\r\n"
    f"Content-Type: image/jpeg\r\n\r\n"
).encode("utf-8")

body = (
    field("chat_id", str(canal)) +
    field("caption", caption) +
    photo_header + img_data +
    f"\r\n--{boundary}--\r\n".encode("utf-8")
)

req = urllib.request.Request(
    f"https://api.telegram.org/bot{token}/sendPhoto",
    data=body,
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
)

try:
    res = urllib.request.urlopen(req)
    data = json.loads(res.read().decode("utf-8"))
    if data.get("ok"):
        print("PUBLICADO EN VIP OK - message_id:", data["result"]["message_id"])
    else:
        print("ERROR:", data)
except urllib.error.HTTPError as e:
    print("HTTP ERROR:", e.read().decode("utf-8"))
