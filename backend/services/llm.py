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
    video_style: str,
    audio_script: str,
    language_vibe: str,
) -> str:
    """Build a fixed visual direction and preserve the retailer's script verbatim."""
    visual_prompts = {
        "showcase": (
            f"Using the provided reference image of {product_reference}, generate a photorealistic, 5-to-7 second cinematic video. "
            "The camera executes a slow, smooth macro-pan across the folded fabric, starting at the border and gliding toward the center. "
            "Keep the background softly blurred with shallow f/2.8 depth of field. Lighting is warm, natural, and earthy, catching the subtle metallic sheen of the weaving. No humans in frame."
        ),
        "model_walk": (
            f"Generate a photorealistic, 7-second fashion video of a beautiful, confident Indian female model wearing the exact {product_reference} shown in the provided reference image. "
            "The model walks slowly toward the camera in a modern, brightly lit indoor boutique. Use a medium-full tracking shot, with fabric draping elegantly and catching light dynamically. 4K fashion editorial style."
        ),
        "dynamic_cut": (
            f"Generate a dynamic, 10-second high-energy fashion video using the provided reference image of {product_reference}. "
            "Scene 1 (0-3s): cinematic close-up of the folded product with a quick zoom into its border and woven detail. "
            "Scene 2 (3-10s): seamless transition to an Indian fashion model wearing the exact same product, twirling playfully in a brightly lit premium retail showroom. Fast-paced, fluid camera movement, ultra-realistic."
        ),
    }
    visual = visual_prompts[video_style]
    return f'{visual} Audio/Dialogue: Generate a {language_vibe} native voiceover that says exactly: "{audio_script.strip()}"'


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
