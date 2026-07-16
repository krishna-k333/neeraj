from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.google_contacts import phone_exists, save_contact, ensure_contact_saved

router = APIRouter()


class ContactRequest(BaseModel):
    phone: str
    name: str = ""


@router.get("/check/{phone}")
async def check_contact(phone: str):
    exists = await phone_exists(phone)
    return {"phone": phone, "exists": exists}


@router.post("/save")
async def save_new_contact(req: ContactRequest):
    try:
        result = await save_contact(req.phone, req.name or None)
        return {"saved": True, "contact": result}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/ensure")
async def ensure_contact(req: ContactRequest):
    """Check + save if missing. Used by thank-you flow."""
    newly_saved = await ensure_contact_saved(req.phone)
    return {"phone": req.phone, "newly_saved": newly_saved}
