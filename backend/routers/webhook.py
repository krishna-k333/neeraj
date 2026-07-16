"""
Vercel / payment system webhook → Thank You WhatsApp message.
Payload: { phone_number: "9XXXXXXXXX", amount_received: "500" }
Also auto-saves customer to Google Contacts if not already there.
"""
import logging
from fastapi import APIRouter, Request, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
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


async def _send_thankyou(phone: str, amount: str, db: AsyncSession):
    """Background: send msg + save contact."""
    clean = phone.replace("+", "").replace(" ", "")
    if not clean.startswith("91"):
        clean = f"91{clean}"

    msg_text = THANKYOU_MSG.format(amount=amount)

    try:
        await evolution.send_text(clean, msg_text, delay=False)
        saved = await ensure_contact_saved(clean)
        record = Message(
            phone=clean,
            direction="outbound",
            content=msg_text,
            status="sent",
            msg_type="thankyou",
        )
        db.add(record)
        await db.commit()
        logger.info(f"Thank-you sent to {clean}, contact newly_saved={saved}")
    except Exception as e:
        logger.error(f"Thank-you failed for {clean}: {e}")


@router.post("/thankyou")
async def thankyou_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Entry point for Vercel/payment webhook."""
    body = await request.json()
    phone = body.get("phone_number") or body.get("phone", "")
    amount = str(body.get("amount_received") or body.get("amount", ""))

    if not phone:
        return {"error": "phone_number required"}

    background_tasks.add_task(_send_thankyou, phone, amount, db)
    return {"queued": True, "phone": phone, "amount": amount}
