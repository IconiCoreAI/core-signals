# Core Signals — CLAUDE.md

Travel companion app for Escape From Reality group trips. Live and login confirmed working at **https://bali.escapefromrealitytravel.com**.

## Status (June 10, 2026)

- ✅ Auth live — Neon + FastAPI JWT + bcrypt (Supabase fully removed)
- ✅ Group chat, documents, SOS wired to backend
- ✅ Gmail SMTP SOS alert deployed via CONTACT_GMAIL credentials
- ✅ Both databases unified on `ep-divine-smoke` (ep-dry-boat retired)
- ✅ 9 traveler accounts created and confirmed in Neon
- ✅ Bali Travel Guide uploaded to R2, registered as `trip_doc`, visible to all travelers
- ✅ Forgot-password code removed from frontend — parked for Firebase migration
- ✅ Admin-reset endpoint built in backend — not yet deployed to Fly
- ✅ Favicon updated to EFR Secondary Logo (white background)
- ✅ Browser tab title updated to "Bali Retirement Trip | Escape From Reality Travel"
- ⬜ Deploy admin-reset endpoint (backend deploy needed)
- ⬜ Regenerate CONTACT_GMAIL_APP_PASSWORD (current one was exposed in chat)
- ⬜ Test all 9 traveler logins end-to-end
- ⬜ Twilio SMS — parked until budget allows (replace vtext gateway when ready)


---

## Stack

| Layer | Tech | Host |
|---|---|---|
| Frontend | React 19 + Vite 8 + Tailwind 4 | Fly.io (`frontend-still-petal-6011`) |
| Backend | FastAPI + uvicorn | Fly.io (`backend-little-leaf-7896`) |
| Database | Neon (Postgres) | `ep-divine-smoke-apn08le7.c-7.us-east-1.aws.neon.tech` |
| File storage | Cloudflare R2 | bucket `efr-travel-docs` |
| Notifications | n8n webhook | `iconicore.app.n8n.cloud` |

---

## Project structure

```
core-signals/
├── backend/
│   ├── main.py          # FastAPI app, CORS, JWT verify, /sos, /health
│   ├── auth.py          # POST /auth/signup, POST /auth/signin (bcrypt + PyJWT)
│   ├── documents.py     # GET /documents, POST /documents/trip|personal, GET /documents/{id}/download
│   ├── messaging.py     # GET|POST /messages/group, GET|POST /messages/private
│   ├── r2.py            # Cloudflare R2 upload/download/delete helpers
│   ├── migrate.py       # One-shot schema migration (run manually)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── fly.toml         # app: backend-little-leaf-7896, region: iad
└── frontend/
    ├── src/
    │   ├── App.jsx       # All screens + auth gate (single-file app)
    │   ├── api.js        # apiFetch helper, localStorage session management
    │   └── main.jsx
    ├── Dockerfile        # Multi-stage: node:20-slim build → gostatic serve
    ├── fly.toml          # app: frontend-still-petal-6011, region: iad
    └── package.json
```

---

## Auth

- **No Supabase** — removed completely (June 2026 session).
- Users sign up/in via `POST /auth/signup` and `POST /auth/signin`.
- Passwords hashed with `bcrypt`. Tokens are HS256 JWTs signed with `JWT_SECRET`, 30-day expiry.
- Frontend stores `cs_token` and `cs_user` in `localStorage`. A 401 response clears session and reloads.
- Users live in the `travelers` table in Neon (`id TEXT, email TEXT, name TEXT, role TEXT, password_hash TEXT`).
- `role = 'admin'` unlocks trip document upload and full document list.

> **Planned:** Migrate auth to Firebase after June 15, 2026. Touch points: `auth.py`, `api.js`, `App.jsx` AuthScreen, `verify_jwt` in `main.py`.

---

## Backend env vars (Fly secrets)

| Var | Purpose |
|---|---|
| `DATABASE_URL` | Neon `ep-divine-smoke` connection string |
| `JWT_SECRET` | HS256 signing key |
| `FERNET_KEY` | Symmetric encryption for private messages |
| `CONTACT_GMAIL_USER` | `contact@escapefromrealitytravelers.com` — SOS email sender |
| `CONTACT_GMAIL_APP_PASSWORD` | Gmail App Password for SMTP — **regenerate, was exposed in chat** |
| `R2_ACCOUNT_ID` | Cloudflare R2 |
| `R2_ACCESS_KEY_ID` | Cloudflare R2 |
| `R2_SECRET_ACCESS_KEY` | Cloudflare R2 |
| `R2_BUCKET_NAME` | `efr-travel-docs` |
| `R2_ENDPOINT` | R2 S3-compatible endpoint |
| `SECURE_INTAKE_SECRET` | Shared secret for `/secure-intake` webhook |

---

## Key endpoints

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/auth/signup` | None | `{email, password, name}` → `{token, user}` |
| POST | `/auth/signin` | None | `{email, password}` → `{token, user}` |
| GET | `/documents` | JWT | Trip docs (visible_to_all) + caller's personal docs |
| POST | `/documents/personal` | JWT | Multipart upload to R2 |
| POST | `/documents/trip` | JWT admin | Multipart upload to R2 |
| GET | `/documents/{id}/download` | JWT | Returns 1-hour presigned R2 URL |
| GET | `/messages/group` | JWT | All group messages, ASC |
| POST | `/messages/group` | JWT | Send group message |
| POST | `/sos` | JWT | Fires n8n webhook + Gmail SMTP via CONTACT_GMAIL → `9124328189@vtext.com` |
| POST | `/admin/reset-password` | Admin JWT | Built, not yet deployed — resets any traveler password |
| POST | `/secure-intake` | Secret | n8n inbound webhook |
| GET | `/health` | None | `{status, database}` |

---

## CORS origins (backend/main.py)

```python
allow_origins=[
    "https://frontend-hikgyujxe-iconi-core-ai.vercel.app",
    "https://frontend-still-petal-6011.fly.dev",
    "https://bali.escapefromrealitytravel.com",
    "http://localhost:5173",
    "http://localhost:4173",
]
```

Add new origins here and redeploy the backend whenever a new frontend URL is introduced.

---

## DNS

`bali.escapefromrealitytravel.com` points to the Fly.io frontend:
- `A` → `66.241.125.248`
- `AAAA` → `2a09:8280:1::124:cedd:0`

TLS cert managed by Fly (`fly certs`).

---

## Deploy

```bash
# Backend
cd backend && flyctl deploy

# Frontend
cd frontend && flyctl deploy

# Both (sequential)
cd backend && flyctl deploy && cd ../frontend && flyctl deploy
```

Frontend Dockerfile does a full `npm ci && npm run build` inside Docker — no local build needed before deploy. `.dockerignore` excludes `node_modules` and `.git`.

---

## Local dev

```bash
# Backend
cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000

# Frontend
cd frontend && npm run dev   # → http://localhost:5173
```

Frontend `.env` points `VITE_API_URL` at the live Fly backend. For local backend testing change it to `http://localhost:8000`.

---

## SOS flow

1. User taps SOS in app → `POST /sos` with `{name, level}`
2. Backend fires n8n webhook (async)
3. Backend sends Gmail SMTP email to `9124328189@vtext.com` (Verizon SMS gateway) via `asyncio.to_thread` using `CONTACT_GMAIL_USER` / `CONTACT_GMAIL_APP_PASSWORD`
4. Email failure is swallowed — SOS response is never blocked by email

---

## Database schema (migrate.py)

Run `python migrate.py` from `backend/` to apply. Safe to re-run (all `CREATE TABLE IF NOT EXISTS` + `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`).

Tables: `travelers`, `channels`, `channel_members`, `messages`, `private_threads`, `private_messages`, `documents`, `triage_log`, `intake_events`, `notifications`.

---

## Forgot Password

Frontend forgot-password flow has been **removed** and is parked until Firebase auth migration (post June 15, 2026). Do not rebuild it against the current bcrypt/JWT stack. When Firebase is in place, use Firebase's native password reset.

---

## Traveler Accounts (Bali 2026)

9 accounts confirmed in Neon `travelers` table. All role = `traveler`. No admin account exists yet — admin features accessible only via direct DB or script.

| Name | Email |
|---|---|
| Pamela Washington | pamscott.w@gmail.com |
| Cindy Notti | cnotti@hotmail.com |
| Veronica Barnes | veronica.barnes25@gmail.com |
| Francine Applewhite | f_applewhite@yahoo.com |
| Lorine Hall | hallaktrans2@gmail.com |
| Lourdes Bernal | lbernal0101@gmail.com |
| Tiana Towns | tianamtowns@gmail.com |
| Cynthia Franklin | cfrankamis@gmail.com |
| Judy Jackson | jackson.jj0507@gmail.com |

---

## Documents (Bali 2026)

Uploaded to R2 bucket `efr-travel-docs` and registered in `documents` table.

| id | Filename | document_type | visible_to_all |
|---|---|---|---|
| 1 | Pam Retirement Bali 2026 Travel Guide .pdf | trip_doc | TRUE |

MASTER OPERATIONS sheet was uploaded then restricted — `visible_to_all = FALSE`. Travelers only see the Travel Guide.

Upload script: `backend/upload_trip_docs.py` — re-run from `backend/` venv to add more documents.

---

## SESSION HANDOFF — June 10, 2026

**PERSONA:** Lilly (backend) + direct DB/R2 ops
**COMPLETED:**
- Unified both Neon databases onto `ep-divine-smoke` — local `.env` and Fly secret both confirmed correct
- Confirmed 9 traveler accounts in Neon (listed above)
- Uploaded Bali Travel Guide PDF to R2, registered as `trip_doc`, `visible_to_all = TRUE`
- Uploaded MASTER OPERATIONS sheet to R2, set `visible_to_all = FALSE` (admin eyes only)
- Updated `document_type` for Travel Guide from `other` to `trip_doc`
- Removed forgot-password UI from frontend — parked for Firebase
- Built admin-reset endpoint in backend — **not yet deployed**
- Switched SOS email credentials from personal Gmail to `contact@escapefromrealitytravelers.com` (CONTACT_GMAIL)
- Updated favicon to EFR Secondary Logo (white background PNG)
- Updated browser tab title to "Bali Retirement Trip | Escape From Reality Travel"
- Frontend deployed 3x to Fly.io — all deploys clean

**NEXT UP:**
1. Deploy backend (`cd backend && flyctl deploy`) to ship admin-reset endpoint
2. Regenerate `CONTACT_GMAIL_APP_PASSWORD` in Google — current one was exposed in chat — update Fly secret immediately
3. Test all 9 traveler logins at https://bali.escapefromrealitytravel.com
4. Verify Travel Guide appears in Docs screen for a traveler account

**BLOCKERS:**
- CONTACT_GMAIL_APP_PASSWORD must be regenerated before SOS can be considered safe
- Admin account does not exist in `travelers` table — trip doc upload via API not possible without one
- Backend machines are on `stopped` state on Fly — will auto-start on first request, but cold start delay possible
