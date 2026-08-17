"""Thank-you page webhook -> WhatsApp message and Google Contact."""
import hmac
import logging
from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from config import settings
from database import SessionLocal
from models import Message
from services import evolution
from services.google_contacts import ensure_contact_saved

router = APIRouter()
logger = logging.getLogger(__name__)

THANKYOU_MSG = """🙏 Neeraj Enterprises से Rs.{amount} की खरीदारी करने के लिए धन्यवाद।

🎥 कृपया हमें इंस्टाग्राम पर फॉलो करें:
https://www.instagram.com/ne_fashionofficial/

✅ Daily Updates:
Follow the NEERAJ ENTERPRISES Fashion SUIT & SAREES channel on WhatsApp:
https://whatsapp.com/channel/0029VbB3ji3ICVfd7aCbhX1o

📍 कृपया अपना अनुभव साझा करें on Google Maps:
https://bit.ly/4tYJGR0"""


async def _send_thankyou(phone: str, amount: str):
    """Background: send the message, save the contact, and record the send."""
    clean = phone.replace("+", "").replace(" ", "")
    if not clean.startswith("91"):
        clean = f"91{clean}"

    msg_text = THANKYOU_MSG.format(amount=amount or "your purchase")

    try:
        await evolution.send_text(clean, msg_text, delay=False)
    except Exception as e:
        logger.error(f"Thank-you failed for {clean}: {e}")
        return

    try:
        saved = await ensure_contact_saved(clean)
    except Exception as e:
        saved = False
        logger.warning(f"Thank-you sent but contact save failed for {clean}: {e}")

    try:
        # Do not reuse the request-scoped DB session in a background task: it is
        # closed as soon as the HTTP response is returned.
        async with SessionLocal() as db:
            db.add(Message(
                phone=clean,
                direction="outbound",
                content=msg_text,
                status="sent",
                msg_type="thankyou",
            ))
            await db.commit()
        logger.info(f"Thank-you sent to {clean}, contact newly_saved={saved}")
    except Exception as e:
        logger.warning(f"Thank-you sent but message history save failed for {clean}: {e}")


async def _read_payload(request: Request) -> dict:
    """Accept JSON, form-urlencoded, or multipart submissions from thank-you pages."""
    content_type = request.headers.get("content-type", "").lower()
    try:
        if "application/json" in content_type:
            payload = await request.json()
        elif "form-urlencoded" in content_type or "multipart/form-data" in content_type:
            payload = dict(await request.form())
        else:
            # Some form builders omit Content-Type; support JSON as a fallback.
            payload = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Send a JSON or form payload") from e
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Payload must be an object")
    return payload


@router.post("/thankyou")
async def thankyou_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
):
    """Queue a thank-you WhatsApp for a completed thank-you/payment page."""
    expected_secret = settings.THANKYOU_WEBHOOK_SECRET.strip()
    if expected_secret and not hmac.compare_digest(
        request.headers.get("x-webhook-secret", "").strip(), expected_secret
    ):
        raise HTTPException(status_code=401, detail="Invalid webhook secret")

    body = await _read_payload(request)
    phone = str(body.get("phone_number") or body.get("phone") or "").strip()
    amount = str(body.get("amount_received") or body.get("amount") or "").strip()

    if not phone:
        raise HTTPException(status_code=422, detail="phone_number required")

    background_tasks.add_task(_send_thankyou, phone, amount)
    return {"queued": True, "phone": phone, "amount": amount}
