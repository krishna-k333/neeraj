"""
AI chatbot client — Hindi/English bilingual WhatsApp replies.
"""
import httpx
from config import settings

AI_BASE = "https://api.sarvam.ai"

SYSTEM_PROMPT = """You are a helpful WhatsApp assistant for Neeraj Enterprises,
an Indian Saree and Ladies Suit shop.

Rules:
- Reply in Hindi (Devanagari script) by default
- If customer writes in English, reply in English
- Be polite, warm, and use 🙏 sometimes
- For product queries, ask what type, color, price range they are looking for
- For pricing, say prices start from ₹X (fill based on catalog)
- Never share personal contact of owner unless asked explicitly
- Keep replies short (under 3 lines for WhatsApp)
- If you can't help, say "हमारे shop पर आएं या call करें"
"""

VIDEO_PROMPT_SYSTEM = """You are an expert AI video director and retail marketing copywriter. Your job is to take basic, vague inputs from a local retailer and convert them into a highly detailed, cinematic image-to-video generation prompt optimized for Gemini Omni Flash.

Output Requirements:
You must return a single, cohesive paragraph that contains both the visual directions and the audio script.
1. Visual Enhancement: Transform the vague product description into a cinematic shot. You must include specific cinematography terms for Shot Composition (e.g. 'Close-up'), Lens & Focus (e.g. 'Macro lens', 'shallow focus'), and Camera Motion (e.g. 'tracking shot', 'pan shot'). Do not describe humans; focus entirely on making the product look premium in a bright retail environment.
2. Audio/Dialogue: Write a punchy, 10-to-15-second spoken script incorporating the offer, location, and contact info. Format this explicitly at the end of the prompt as 'Audio/Dialogue: [Script]'.

Output Format Example:
'A cinematic, ultra-realistic close-up macro shot of a vibrant [Enhanced Product Description], resting on a clean display table in a brightly lit, premium retail boutique. The camera executes a slow, smooth tracking shot across the intricate fabric details, with a shallow depth of field blurring the neatly stacked shelves in the background. Audio/Dialogue: Generate an energetic native voiceover in [Language] that says: "[Generated Script]"'

Return ONLY the final prompt paragraph. No preamble, no markdown, no quotes around the whole thing."""


async def generate_video_prompt(
    product_reference: str,
    offer_hook: str,
    location_contact: str,
    language_vibe: str,
) -> str:
    """Turn structured retailer inputs into a cinematic image-to-video prompt via the master prompt above."""
    user_message = (
        f"Product Reference: {product_reference}\n"
        f"Offer/Hook: {offer_hook}\n"
        f"Location/Contact: {location_contact}\n"
        f"Language/Vibe: {language_vibe}"
    )

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            f"{AI_BASE}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.AI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.AI_MODEL,
                "messages": [
                    {"role": "system", "content": VIDEO_PROMPT_SYSTEM},
                    {"role": "user", "content": user_message},
                ],
                "max_tokens": 400,
                "temperature": 0.8,
            }
        )
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()


async def chat(user_message: str, history: list[dict] = None) -> str:
    """Get AI reply for a WhatsApp message."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history[-6:])  # last 3 turns context
    messages.append({"role": "user", "content": user_message})

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            f"{AI_BASE}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.AI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.AI_MODEL,
                "messages": messages,
                "max_tokens": 300,
                "temperature": 0.7,
            }
        )
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]
