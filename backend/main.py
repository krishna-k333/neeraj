from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import init_db
from routers import catalog, whatsapp, broadcast, social, video, dashboard, webhook, contacts

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="Neeraj Unified Dashboard API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(catalog.router, prefix="/api/catalog", tags=["Catalog"])
app.include_router(whatsapp.router, prefix="/api/whatsapp", tags=["WhatsApp"])
app.include_router(broadcast.router, prefix="/api/broadcast", tags=["Broadcast"])
app.include_router(social.router, prefix="/api/social", tags=["Social"])
app.include_router(video.router, prefix="/api/video", tags=["Video"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(webhook.router, prefix="/api/webhook", tags=["Webhook"])
app.include_router(contacts.router, prefix="/api/contacts", tags=["Contacts"])

@app.get("/health")
async def health():
    return {"status": "ok", "service": "neeraj-dashboard"}
