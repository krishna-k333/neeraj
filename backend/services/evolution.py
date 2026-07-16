"""
Evolution API client — WhatsApp messaging via REST.
Anti-block: random 2.5–5s delay between messages.
"""
import httpx
import asyncio
import random
from config import settings

BASE = settings.EVOLUTION_API_URL
INSTANCE = settings.EVOLUTION_INSTANCE
HEADERS = {"apikey": settings.EVOLUTION_API_KEY, "Content-Type": "application/json"}


async def _post(path: str, body: dict) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{BASE}{path}", json=body, headers=HEADERS)
        r.raise_for_status()
        return r.json()


async def random_delay():
    """Anti-block: wait 2.5–5 seconds between sends."""
    await asyncio.sleep(random.uniform(2.5, 5.0))


async def send_text(phone: str, text: str, delay: bool = True) -> dict:
    """Send plain text message. phone = '91XXXXXXXXXX'"""
    if delay:
        await random_delay()
    return await _post(f"/message/sendText/{INSTANCE}", {
        "number": phone,
        "text": text,
        "linkpreview": True,
    })


async def send_image(phone: str, image_url: str, caption: str = "", delay: bool = True) -> dict:
    if delay:
        await random_delay()
    return await _post(f"/message/sendMedia/{INSTANCE}", {
        "number": phone,
        "mediatype": "image",
        "media": image_url,
        "caption": caption,
    })


async def send_video(phone: str, video_url: str, caption: str = "", delay: bool = True) -> dict:
    if delay:
        await random_delay()
    return await _post(f"/message/sendMedia/{INSTANCE}", {
        "number": phone,
        "mediatype": "video",
        "media": video_url,
        "caption": caption,
    })


async def get_media_base64(message_id: str) -> tuple[str, str]:
    """
    Fetch the raw media of an inbound message as base64.
    Returns (base64_data, mimetype). Used to hand customer photos to Gemini.
    """
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            f"{BASE}/chat/getBase64FromMediaMessage/{INSTANCE}",
            json={"message": {"key": {"id": message_id}}, "convertToMp4": False},
            headers=HEADERS,
        )
        r.raise_for_status()
        data = r.json()
    return data.get("base64", ""), data.get("mimetype", "image/jpeg")


async def get_instance_status() -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(
            f"{BASE}/instance/connectionState/{INSTANCE}",
            headers=HEADERS
        )
        return r.json()
