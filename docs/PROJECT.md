# Neeraj Unified Dashboard

**Client:** Neeraj Enterprises — Indian Saree & Ladies Suit Wholesale/Retail  
**Location:** Local shop, India  
**Built by:** Krishna (AI OS)

---

## Overview

A full-stack business automation platform deployable on EasyPanel. Gives the client one dashboard to manage all customer communication, social media, video creation, and product catalog.

---

## Modules

### 1. Product Catalog
- Upload images/videos of sarees and suits
- Tag by category, color, price range
- Storage: Cloudinary (primary) or Google Drive fallback
- Used as reference for WhatsApp replies, social posts, and video generation

### 2. WhatsApp Automation (Evolution API)
**Inbound:** AI chatbot powered by Sarvam AI LLM responds to customer queries
- Recognizes product image requests → pulls from catalog
- Handles FAQs, pricing, availability

**Outbound Broadcast:** Smart rate-limited message sender
- **Warming Schedule:**
  - Days 1–3: 0 outbound (inbound replies only)
  - Days 4–7: max 150 msgs/day
  - Week 2: max 400 msgs/day  
  - Week 3: max 1,000 msgs/day
  - Week 4+: max 2,000 msgs/day (hard cap)
- **Anti-block delays:** 2.5–5 sec random between each message
- Total daily limit (inbound + outbound) enforced

### 3. Social Media Scheduler (Postiz)
- Self-hosted Postiz integration
- Schedule posts to Instagram, YouTube, Facebook
- Pull catalog images as post media
- View all scheduled/published posts in dashboard

### 4. Video Generator (kie.ai)
- Generate product showcase videos via kie.ai Omni/Gemini model
- Input: catalog image + caption → output: short video
- Videos saved to Cloudinary, ready for Reels/Shorts

### 5. Thank You Message Sender
- Triggered by webhook (from payment system / Vercel webhook)
- Sends personalized Hindi thank-you WhatsApp message
- Checks if customer number exists in Google Contacts
  - Not found → auto-saves with name "Customer" + date
- Uses n8n workflow (existing workflow as base)

### 6. Unified Dashboard
- Today's stats: messages sent, posts published, videos made, replies handled
- Catalog browser with quick-upload
- Broadcast composer
- Warming schedule status display
- Recent activity feed

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python) |
| Frontend | Next.js 14 (App Router) |
| Database | SQLite (via Turso/libsql for EasyPanel) |
| LLM | Sarvam AI |
| WhatsApp | Evolution API |
| Media Storage | Cloudinary |
| Social | Postiz (self-hosted) |
| Video | kie.ai API |
| Automation | n8n |
| Deployment | EasyPanel (Docker Compose) |

---

## Evolution API Credentials
- Host: `http://whats-evolution-api.vvbe62.easypanel.host`
- Instance: `neeraj1`
- API Key: `429683C4C977415CAAFCCE10F7D57E11`

---

## Webhook Reference
- Thank-you webhook path: `98d5228d-32e5-4064-84fd-af63ad59cee2`
- Payload: `{ phone_number, amount_received }`

---

## Warming Schedule Logic

```
Account age → Max daily outbound
0–3 days    → 0 (listen only)
4–7 days    → 150
8–14 days   → 400
15–21 days  → 1000
22+ days    → 2000 (permanent cap)
```
