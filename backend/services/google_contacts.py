"""
Google Contacts integration.
Check if phone exists → if not, auto-save as new contact.
"""
import httpx
from config import settings
from datetime import datetime

TOKEN_URL = "https://oauth2.googleapis.com/token"
PEOPLE_API = "https://people.googleapis.com/v1"


async def _get_access_token() -> str:
    async with httpx.AsyncClient() as client:
        r = await client.post(TOKEN_URL, data={
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "refresh_token": settings.GOOGLE_REFRESH_TOKEN,
            "grant_type": "refresh_token",
        })
        r.raise_for_status()
        return r.json()["access_token"]


async def phone_exists(phone: str) -> bool:
    """Check if a phone number is already in Google Contacts."""
    token = await _get_access_token()
    # Search contacts by phone — use searchContacts API
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{PEOPLE_API}/people:searchContacts",
            headers={"Authorization": f"Bearer {token}"},
            params={
                "query": phone,
                "readMask": "phoneNumbers,names",
                "pageSize": 5,
            }
        )
        if r.status_code == 200:
            results = r.json().get("results", [])
            for result in results:
                for ph in result.get("person", {}).get("phoneNumbers", []):
                    clean = ph.get("value", "").replace(" ", "").replace("-", "")
                    if phone.replace("+", "") in clean.replace("+", ""):
                        return True
    return False


async def save_contact(phone: str, name: str = None) -> dict:
    """Save a new contact. Auto-name as 'Customer DD-Mon-YYYY' if no name given."""
    token = await _get_access_token()
    if not name:
        name = f"Customer {datetime.now().strftime('%d-%b-%Y')}"

    body = {
        "names": [{"givenName": name}],
        "phoneNumbers": [{"value": phone, "type": "mobile"}],
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{PEOPLE_API}/people:createContact",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=body,
        )
        r.raise_for_status()
        return r.json()


async def ensure_contact_saved(phone: str) -> bool:
    """Check if contact exists. If not, save it. Returns True if newly saved."""
    exists = await phone_exists(phone)
    if not exists:
        await save_contact(phone)
        return True
    return False
