# Core Signals — CLAUDE.md

Travel companion app for Escape From Reality group trips. Live at **https://bali.escapefromrealitytravel.com**.

---

## Live Status (June 16, 2026)

- App live at `bali.escapefromrealitytravel.com` and `frontend-still-petal-6011.fly.dev`
- Backend live at `backend-little-leaf-7896.fly.dev`
- Custom domain DNS verified via Namecheap A + AAAA records
- Auth: Neon + FastAPI JWT + bcrypt (Supabase fully removed)
- Database: `ep-divine-smoke` (Neon) — all 9 travelers confirmed
- 9 traveler accounts, temporary password `Bali2026!`
- R2 bucket `efr-travel-docs` is **PRIVATE** — all documents served via 1-hour presigned URLs
- Token `efr-travel-docs-token-2` (Object Read + Write) signs presigned GET URLs
- Trip documents visible to all travelers: Bali Travel Guide PDF (id=1), Mulia Bali Lunch Confirmation (id=4)
- SOS working via Gmail SMTP + vtext gateway (Verizon) to `9124328189@vtext.com`
- Admin-reset endpoint live at `POST /auth/admin-reset`, secured with `ADMIN_RESET_TOKEN`
- PWA manifest live — travelers can install via "Add to Home Screen" (Safari/Chrome)
- Tab title: `Bali Retirement Trip | Escape From Reality Travel`
- Favicon: EFR R logo (white background)
- Change password + Change name: both working via in-app header links
- Group chat shows traveler first names (joined from travelers table)

---

## Security Notes

- All secrets managed via `read -s` in plain Mac terminal — values never visible in terminal or chat
- `JWT_SECRET` and `FERNET_KEY` are **NOT** in Fly secrets — backend uses hardcoded defaults. Accepted by Monet for now (sole operator, private access). Set before any multi-user admin access is added.
- `ADMIN_RESET_TOKEN` was exposed in June 10 chat — regenerate before next use
- June 10 evening: full `backend/.env` was read into chat. Credentials needing rotation before June 24 launch: Neon `DATABASE_URL` password, `JWT_SECRET`, `FERNET_KEY`, `R2_ACCESS_KEY_ID`/`R2_SECRET_ACCESS_KEY`, `CONTACT_GMAIL_APP_PASSWORD`, `ADMIN_RESET_TOKEN`
- ITS project does NOT share this project's Neon database or credentials — separate Neon project at `~/its/CLAUDE.md`
- `.env` is gitignored, secrets are never committed to the repo
- `admin_access_granted` field exists on documents table but is NOT yet enforced in the download endpoint — admin can currently open any traveler's personal document. Fix is: check `admin_access_granted` in `GET /documents/{id}/download` before generating presigned URL.

---

## Stack

| Layer | Tech | Host |
|---|---|---|
| Frontend | React 19 + Vite 8 + Tailwind 4 | Fly.io (`frontend-still-petal-6011`) |
| Backend | FastAPI + uvicorn | Fly.io (`backend-little-leaf-7896`) |
| Database | Neon (Postgres) | `ep-divine-smoke-apn08le7.c-7.us-east-1.aws.neon.tech` |
| File storage | Cloudflare R2 | bucket `efr-travel-docs` (private) |
| Notifications | n8n webhook | `iconicore.app.n8n.cloud` |

---

## Project Structure

```
core-signals/
backend/
    main.py              FastAPI app, CORS, JWT verify, /sos, /health
    auth.py              /auth/signup, /auth/signin, /auth/change-password, /auth/update-name, /auth/admin-reset
    documents.py         GET /documents, POST /documents/trip|personal, GET /documents/{id}/download
    messaging.py         GET|POST /messages/group (includes sender_name join), GET|POST /messages/private
    r2.py                Cloudflare R2 upload/presigned-URL/delete helpers
    migrate.py           One-shot schema migration (run manually)
    send_welcome.py      Gmail SMTP welcome email script (dry run default, --send to deliver)
    upload_trip_docs.py  One-shot script to register R2 docs in Neon
    requirements.txt
    Dockerfile
    fly.toml             app: backend-little-leaf-7896, region: iad
frontend/
    src/
        App.jsx          All screens + auth gate (single-file app)
        api.js           apiFetch helper, localStorage session management
        main.jsx
    public/
        favicon.png      EFR R logo
        manifest.json    PWA manifest — enables Add to Home Screen
    index.html           PWA meta tags (apple-mobile-web-app-*, theme-color, manifest link)
    Dockerfile           Multi-stage: node:20-slim build + gostatic serve
    fly.toml             app: frontend-still-petal-6011, region: iad
    package.json
```

---

## Auth

- No Supabase. Removed completely June 2026.
- Users sign in via `POST /auth/signin`. Passwords hashed with bcrypt. Tokens are HS256 JWTs signed with `JWT_SECRET`, 30-day expiry.
- Frontend stores `cs_token` and `cs_user` in `localStorage`. A 401 from a protected endpoint clears session and reloads. A 401 from `/auth/*` throws the error message so the form can display it.
- Users live in the `travelers` table in Neon (`id TEXT, email TEXT, name TEXT, role TEXT, password_hash TEXT`).
- `role = 'admin'` unlocks trip document upload and full document list.
- Admin password reset (no frontend): `POST /auth/admin-reset` with `X-Admin-Token` header.
- Name change: `PATCH /auth/update-name` with `{name}` — updates DB and returns updated user object for localStorage refresh.

> **Planned:** Migrate auth to Firebase after June 15, 2026 (now deferred). Touch points: `auth.py`, `api.js`, `App.jsx` AuthScreen, `verify_jwt` in `main.py`.

---

## Traveler Accounts (ep-divine-smoke)

| Name | Email | Role |
|---|---|---|
| Pamela Washington | pamscott.w@gmail.com | traveler |
| Cindy Notti | cnotti@hotmail.com | traveler |
| Veronica Barnes | veronica.barnes25@gmail.com | traveler |
| Francine Applewhite | f_applewhite@yahoo.com | traveler |
| Lorine Hall | hallaktrans2@gmail.com | traveler |
| Lourdes Bernal | lbernal0101@gmail.com | traveler |
| Tiana Towns | tianamtowns@gmail.com | traveler |
| Cynthia Franklin | cfrankamis@gmail.com | traveler |
| Judy Jackson | jackson.jj0507@gmail.com | traveler |

Note: Carla Kirkland travels with the group but has no email address and no app account. She receives information through other travelers.

All accounts use temporary password `Bali2026!`. Travelers can change name and password via in-app header links.

---

## Backend Env Vars (Fly Secrets)

Confirmed deployed as of June 16, 2026:

| Var | Status | Purpose |
|---|---|---|
| `DATABASE_URL` | Deployed | Neon ep-divine-smoke connection string |
| `GMAIL_USER` | Deployed | `monetplanter@gmail.com` — SOS email sender |
| `GMAIL_APP_PASSWORD` | Deployed | Gmail app password for GMAIL_USER |
| `CONTACT_GMAIL_USER` | Deployed | `contact@escapefromrealitytravelers.com` |
| `CONTACT_GMAIL_APP_PASSWORD` | Deployed | Gmail app password for CONTACT_GMAIL_USER |
| `ADMIN_RESET_TOKEN` | Deployed | Shared secret for `/auth/admin-reset` — regenerate before next use |
| `BALI_API_KEY` | Deployed | Used by admin_api.py — constant-time compare auth |
| `R2_ACCOUNT_ID` | Deployed | Cloudflare account ID — also builds R2_ENDPOINT automatically |
| `R2_ACCESS_KEY_ID` | Deployed | efr-travel-docs-token-2 key |
| `R2_SECRET_ACCESS_KEY` | Deployed | efr-travel-docs-token-2 secret |
| `R2_BUCKET_NAME` | Deployed | `efr-travel-docs` |
| `JWT_SECRET` | **NOT SET** | Falls back to `"default_jwt_secret"` — accepted by Monet |
| `FERNET_KEY` | **NOT SET** | Private messages raise 500 if called — feature not in active use |
| `R2_ENDPOINT` | **NOT SET** | Constructed automatically: `https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com` |

---

## Key Endpoints

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/auth/signup` | None | `{email, password, name}` returns `{token, user}` |
| POST | `/auth/signin` | None | `{email, password}` returns `{token, user}` |
| POST | `/auth/change-password` | JWT | `{current_password, new_password}` |
| PATCH | `/auth/update-name` | JWT | `{name}` — updates travelers table, returns updated user |
| POST | `/auth/admin-reset` | X-Admin-Token header | `{email, new_password}` — Monet only, no frontend |
| GET | `/documents` | JWT | Trip docs (visible_to_all) + caller's personal docs |
| POST | `/documents/personal` | JWT | Multipart upload to R2 |
| POST | `/documents/trip` | JWT admin | Multipart upload to R2 |
| GET | `/documents/{id}/download` | JWT | Returns 1-hour presigned R2 URL — checks owner or visible_to_all |
| GET | `/messages/group` | JWT | All group messages ASC, includes `sender_name` |
| POST | `/messages/group` | JWT | Send group message |
| POST | `/sos` | JWT | Fires n8n webhook + Gmail SMTP to `9124328189@vtext.com` |
| POST | `/secure-intake` | Secret | n8n inbound webhook |
| GET | `/health` | None | `{status, database}` |

---

## Document Serving (R2)

Bucket `efr-travel-docs` is **private** — public access is disabled by design (travelers have personal docs like visas that must not be world-readable).

Flow:
1. `GET /documents` returns document metadata (id, filename, type) — no URLs
2. Traveler taps "Open" → frontend calls `GET /documents/{id}/download`
3. Backend verifies JWT, checks `is_admin OR uploaded_by == user OR visible_to_all`
4. If authorized: calls `generate_presigned_url(key, expires_in=3600)` via boto3
5. Returns `{url, expires_in: 3600}` — frontend opens in new tab
6. URL is valid for 1 hour, signed with efr-travel-docs-token-2 credentials

**Admin access gap (known):** `admin_access_granted` field exists in documents table but the download endpoint does not check it. Admin can currently generate presigned URLs for any document including travelers' personal files. Fix: add `admin_access_granted` check in `documents.py` download endpoint.

---

## Trip Documents (database state as of June 16, 2026)

| id | Filename | Type | Visible to all |
|---|---|---|---|
| 1 | Pam Retirement Bali 2026 Travel Guide .pdf | trip_doc | YES |
| 4 | Mulia Bali Lunch Confirmation.pdf | trip_doc | YES |

Cynthia Franklin has 1 personal document (Visa Indonesia.pdf, id=2). All other travelers have 0 personal docs.

---

## Hotel & Transfers Screen

Accessible from Home > Quick Access > "Hotel & transfers". Shows:

- **Hotel:** Taman Dharmawangsa Suites
- **Room:** Two Bedroom Pool Villa, Daily Breakfast Included
- **Address:** Jl. Astina Pura No.1, Jl. Raya Kampial, Nusa Dua, Benoa, Kecamatan Kuta Selatan, Badung, Bali, Indonesia 80361
- **Phone/WhatsApp:** +62 81 138 017 999

Airport pickups:
- June 23: Francine Applewhite + Lorine Hall / Korean Airlines KE633, ETA 11:50pm / 1x MPV
- June 24 (CX783 5:40pm): Pam, Cindy, Veronica, Carla, Lourdes, Tiana, Judy / 2x MPV
- June 24 (SQ938 12:00pm): Cynthia Franklin / 1x MPV
- Note: Driver meets at arrival gate. Transfer trouble: WhatsApp +62 81 138 017 999

---

## PWA Install Instructions (for travelers)

**iPhone:** Safari → bali.escapefromrealitytravel.com → Share button → "Add to Home Screen" → Add

**Android:** Chrome → same URL → three dots menu → "Add to Home Screen"

App installs with teal EFR icon, opens fullscreen, no browser bar. No App Store required.

---

## CORS Origins (backend/main.py)

```python
allow_origins=[
    "https://frontend-hikgyujxe-iconi-core-ai.vercel.app",
    "https://frontend-still-petal-6011.fly.dev",
    "https://bali.escapefromrealitytravel.com",
    "http://localhost:5173",
    "http://localhost:4173",
]
```

---

## DNS

`bali.escapefromrealitytravel.com` points to the Fly.io frontend (verified via Namecheap):
- `A` record: `66.241.125.248`
- `AAAA` record: `2a09:8280:1::124:cedd:0`

TLS cert managed by Fly (`fly certs`).

---

## Deploy

```bash
# Backend
cd backend && flyctl deploy

# Frontend
cd frontend && flyctl deploy

# Both in parallel (from repo root)
flyctl deploy & cd frontend && flyctl deploy
```

Frontend Dockerfile does a full `npm ci && npm run build` inside Docker. No local build needed before deploy.

---

## Local Dev

Local `.env` credentials are stale as of June 16 — R2 and DATABASE_URL no longer match Fly secrets. Use the live API or fly ssh for any database/R2 operations.

```bash
# Backend
cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000

# Frontend
cd frontend && npm run dev   # http://localhost:5173
```

---

## Admin Password Reset (curl)

```bash
curl -X POST https://backend-little-leaf-7896.fly.dev/auth/admin-reset \
  -H "Content-Type: application/json" \
  -H "X-Admin-Token: <ADMIN_RESET_TOKEN>" \
  -d '{"email": "traveler@example.com", "new_password": "NewPassword123"}'
```

---

## One-Shot DB/R2 Operations via Fly SSH

Local `.env` is stale. For direct DB queries or R2 uploads use fly ssh:

```bash
# Wake the backend
curl -s https://backend-little-leaf-7896.fly.dev/health

# Open SSH shell
flyctl ssh console -a backend-little-leaf-7896

# Transfer a file to the machine
flyctl ssh sftp shell -a backend-little-leaf-7896
# then: put /local/path /tmp/filename

# Run a script (reads credentials from uvicorn process /proc environ)
flyctl ssh console -a backend-little-leaf-7896 -C "python3 /tmp/script.py"
```

Scripts running on the fly machine should read credentials from the uvicorn process environment (scan `/proc/*/environ` for `R2_BUCKET_NAME` to find the right PID).

---

## SOS Flow

1. Traveler taps SOS and confirms the dialog
2. App calls `POST /sos` with `{level: "HIGH"}`
3. Backend fires n8n webhook (async, non-blocking)
4. Backend sends Gmail SMTP email to `9124328189@vtext.com` (Verizon SMS gateway)
5. Email failure is swallowed so SOS response is never blocked

---

## Database Schema (migrate.py)

Run `python migrate.py` from `backend/` to apply. Safe to re-run.

Tables: `travelers`, `channels`, `channel_members`, `messages`, `private_threads`, `private_messages`, `documents`, `triage_log`, `intake_events`, `notifications`.

---

## Persona Team

| Persona | Role |
|---|---|
| **Missy** | Chief of Staff. Session flow, prioritization, protects Monet's bandwidth. |
| **Lilly** | Systems Architect. Backend, database, system integrity. Approves before every deploy. |
| **Martin** | Execution Tutor. Frontend, step-by-step implementation. Deploys after Lilly signs off. |
| **Daniel** | Risk Awareness Advisor. Security review before every commit and deploy. |
| **Erika + Cassie** | Client-facing only. Do not participate in builds. |

---

## Rules — Never Break

- Stack locked: React, FastAPI, Neon, Fly.io. No substitutions without Monet's explicit approval.
- Square ONLY for payments. Never Stripe.
- No Vercel. No Supabase.
- No em dashes or hyphens used as punctuation in any output.
- Monet is architect, Claude is builder. No unsolicited refactors.
- Daniel reviews before every commit. Lilly approves before every deploy.

---

## Open Items

- Enforce `admin_access_granted` in `GET /documents/{id}/download` — admin currently bypasses, sees all personal docs
- Set `JWT_SECRET` and `FERNET_KEY` as Fly secrets before any multi-admin use or before enabling private messages
- Regenerate `ADMIN_RESET_TOKEN` (exposed in June 10 chat) and update Fly secret before next use
- Firebase auth migration deferred — remove parked forgot-password code when Firebase goes live
- Twilio parked until budget allows. SOS uses vtext gateway for now.
- Test all 9 traveler logins at live webinar June 24
