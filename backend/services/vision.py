"""
Gemini vision — "sees" inbound customer photos and returns a short factual
description. Sarvam can't process images, so Gemini acts as the eyes: it
describes the saree/suit in the photo, and that description is fed into the
normal Sarvam text pipeline which writes the actual Hindi reply.
"""
import logging

import httpx

from config import settings

logger = logging.getLogger(__name__)

GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

# Kept tight and factual — this text becomes context for the Sarvam reply,
# it is NOT sent to the customer directly.
_DESCRIBE_PROMPT = (
    "You are helping a WhatsApp assistant for an Indian saree and ladies suit shop. "
    "A customer sent this photo. In 1-2 short sentences, describe only what is "
    "relevant to the shop: garment type (saree / suit / dupatta / lehenga / other), "
    "dominant colours, fabric or pattern if visible, and any obvious style details. "
    "If it is not clothing, say briefly what it is. Do not greet, do not add opinions."
)


async def describe_image(base64_data: str, mimetype: str, caption: str = "") -> str:
    """
    Return a short factual description of the image, or "" on failure.
    `caption` is the customer's text on the photo, if any.
    """
    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not set — cannot process inbound image")
        return ""
    if not base64_data:
        return ""

    prompt = _DESCRIBE_PROMPT
    if caption:
        prompt += f'\n\nThe customer wrote with the photo: "{caption}"'

    url = f"{GEMINI_BASE}/{settings.GEMINI_MODEL}:generateContent"
    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": mimetype, "data": base64_data}},
                ]
            }
        ]
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                url,
                params={"key": settings.GEMINI_API_KEY},
                json=body,
            )
            r.raise_for_status()
            data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        logger.error(f"Gemini vision error: {e}")
        return ""
