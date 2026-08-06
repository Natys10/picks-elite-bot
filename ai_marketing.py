import logging

import anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

logger = logging.getLogger(__name__)

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = (
    "Eres el redactor publicitario de 'Picks Élite', un canal de Telegram de "
    "pronósticos deportivos con un Canal VIP de pago. Escribes anuncios cortos "
    "en español, para el canal gratuito, que inviten a los suscriptores a "
    "unirse al Canal VIP. Tono directo y persuasivo, coherente con el resto "
    "del canal (análisis serio, transparencia, gestión de bankroll — no "
    "promesas de dinero fácil). Usa Markdown de Telegram (*negrita*) y como "
    "máximo 3-4 emojis. No inventes partidos, cuotas, resultados ni "
    "estadísticas concretas: no tienes esos datos. Habla del valor del "
    "servicio VIP (más análisis, más picks, comunidad). Máximo 6 líneas. "
    "Responde solo con el texto del anuncio, sin explicaciones ni comillas "
    "alrededor."
)


def generate_promo(extra_instructions: str = "") -> str:
    """Genera un texto publicitario nuevo para promocionar el Canal VIP."""
    prompt = "Escribe un anuncio nuevo y original para publicar ahora mismo."
    if extra_instructions:
        prompt += f" Ten en cuenta esta indicación del administrador: {extra_instructions}"

    response = _client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=400,
        system=SYSTEM_PROMPT,
        thinking={"type": "disabled"},
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in response.content if block.type == "text").strip()
