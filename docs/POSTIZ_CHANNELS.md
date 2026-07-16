# Connecting Social Channels to Postiz

Postiz (self-hosted, `easypanel/docker-compose.yml`) handles all OAuth with each
platform. The dashboard backend (`backend/routers/social.py`) only calls Postiz's
`/api/posts` with a `platform` string — it never talks to Meta/Google directly.

Two steps for every channel: (1) set env vars so Postiz's OAuth app exists, (2)
connect the channel from Postiz's own "Add Channel" UI at `http://<postiz-host>:5000`.

## 1. Instagram

- Meta for Developers app → create app, type **Other**, category **Business**.
- Two connection modes (pick one):
  - **Facebook Business** (recommended, lets you also run Facebook): scopes
    `instagram_basic, pages_show_list, pages_read_engagement, business_management,
    instagram_content_publish, instagram_manage_comments, instagram_manage_insights`
    → set `FACEBOOK_APP_ID` / `FACEBOOK_APP_SECRET`.
  - **Standalone**: Instagram Business Login → set `INSTAGRAM_APP_ID` / `INSTAGRAM_APP_SECRET`.
- Redirect URI: `https://<postiz-domain>/integrations/social/instagram[standalone]`
- Supports: feed posts (image/carousel/video/Reels), Stories. Not supported: story link stickers, auto comment-reply.
- Common error: "Insufficient developer role" → add the IG account as an app tester and accept the invite in Instagram settings.

## 2. Facebook

- Same Meta app as Instagram (one app can serve both).
- Business portfolio + business verification required for public/live apps.
- Scopes: `pages_show_list, business_management, pages_manage_posts,
  pages_manage_engagement, pages_read_engagement, read_insights`
- Env vars: `FACEBOOK_APP_ID`, `FACEBOOK_APP_SECRET` (shared with Instagram).
- Redirect URI: `https://<postiz-domain>/integrations/social/facebook`
- **Must switch the Meta app to Live mode** — in Development mode, posted media is only visible to app testers/developers.

## 3. Google My Business

- Google Cloud project → enable: Google My Business API, My Business Account Management API, My Business Business Information API.
- Google My Business API access requires a manual approval request (Google's [access request form](https://developers.google.com/my-business/content/prereqs#request-access)) — takes days to a week.
- OAuth consent screen: External user type.
- Env vars: `POSTIZ_GOOGLE_CLIENT_ID` / `POSTIZ_GOOGLE_CLIENT_SECRET` (mapped to Postiz's `GOOGLE_CLIENT_ID`/`SECRET` in docker-compose — kept separate from the backend's own Google Contacts credentials).
- Redirect URI: `https://<postiz-domain>/integrations/social/google`
- Analytics for newly verified profiles may show empty data — this is normal, not a bug.

## 4. YouTube

- Same or separate Google Cloud project → enable: YouTube Data API v3, YouTube Analytics API, YouTube Reporting API.
- OAuth client type: Web application. Add yourself as a test user in the consent screen.
- Uses the same `POSTIZ_GOOGLE_CLIENT_ID` / `POSTIZ_GOOGLE_CLIENT_SECRET` as Google My Business (one Google Cloud OAuth client can back both, as long as all required APIs are enabled on it).
- Redirect URI: `https://<postiz-domain>/integrations/social/youtube`
- **Brand accounts**: set app status to External, add yourself as test user, then add the app to trusted apps in Google Workspace Admin — allow ~5 hours before connecting.

## Applying config

1. Copy `easypanel/.env.example` → `easypanel/.env`, fill in the values above.
2. `docker compose -f easypanel/docker-compose.yml up -d` to restart Postiz with the new env vars.
3. Open the Postiz UI → Add Channel → complete the OAuth flow for each platform.
4. Once connected, the dashboard's Social page (`frontend/components/pages/SocialPage.tsx`) can fan a single post out to any combination of `instagram`, `youtube`, `facebook`, `google_my_business` via `POST /schedule` on the backend.

**Note:** verify `google_my_business` is the exact platform identifier Postiz expects in its API before going live — check Postiz's `/integrations` list endpoint or dashboard once Google is connected, and update `VALID_PLATFORMS` in `backend/routers/social.py` if it differs.
