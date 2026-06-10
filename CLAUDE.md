# Core Signals — CLAUDE.md

Travel companion app for Escape From Reality group trips. Live at **https://bali.escapefromrealitytravel.com**.

---

## Live Status (June 10, 2026)

- App live at `bali.escapefromrealitytravel.com` and `frontend-still-petal-6011.fly.dev`
- Backend live at `backend-little-leaf-7896.fly.dev`
- Custom domain DNS verified via Namecheap A + AAAA records
- Auth: Neon + FastAPI JWT + bcrypt (Supabase fully removed)
- Database: `ep-divine-smoke` (Neon) — all 9 travelers migrated here, ep-dry-boat retired
- 9 traveler accounts created, password `Bali2026!`, all confirmed in ep-divine-smoke
- Bali Travel Guide PDF uploaded to R2, registered as `trip_doc`, `visible_to_all=TRUE`
- Master Operations sheet hidden from travelers (`visible_to_all=FALSE`)
- SOS working via Gmail SMTP + vtext gateway (Verizon) to `9124328189@vtext.com`
- Admin-reset endpoint live at `POST /auth/admin-reset`, secured with `ADMIN_RESET_TOKEN`
- Forgot-password flow parked — remove after Firebase migration post June 15
- Tab title: `Bali Retirement Trip | Escape From Reality Travel`
- Favicon: EFR R logo (white background)
- Change password: working via in-app header link

---

## Security Notes

- Both Gmail app passwords (`GMAIL_APP_PASSWORD` and `CONTACT_GMAIL_APP_PASSWORD`) were exposed in Claude Code chat during a prior session
- Both were regenerated and updated using `read -s PASS` in plain Mac terminal so the value was never visible in any terminal or chat
- `ADMIN_RESET_TOKEN` was also exposed in chat during June 10 session — regenerate and update Fly secret before next use
- `.env` is gitignored, secrets are never committed to the repo

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

## Project Structure

```
core-signals/
backend/
    main.py              FastAPI app, CORS, JWT verify, /sos, /health
    auth.py              /auth/signup, /auth/signin, /auth/change-password, /auth/admin-reset
    documents.py         GET /documents, POST /documents/trip|personal, GET /documents/{id}/download
    messaging.py         GET|POST /messages/group, GET|POST /messages/private
    r2.py                Cloudflare R2 upload/download/delete helpers
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

> **Planned:** Migrate auth to Firebase after June 15, 2026. Touch points: `auth.py`, `api.js`, `App.jsx` AuthScreen, `verify_jwt` in `main.py`. Forgot-password code is parked and should be removed once Firebase is live.

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

All accounts use temporary password `Bali2026!`. Travelers are prompted to change it on first login.

---

## Backend Env Vars (Fly Secrets)

| Var | Purpose |
|---|---|
| `DATABASE_URL` | Neon ep-divine-smoke connection string |
| `JWT_SECRET` | HS256 signing key |
| `FERNET_KEY` | Symmetric encryption for private messages |
| `GMAIL_USER` | `monetplanter@gmail.com` — SOS email sender |
| `GMAIL_APP_PASSWORD` | Gmail app password for GMAIL_USER — regenerated June 10 |
| `CONTACT_GMAIL_USER` | `contact@escapefromrealitytravelers.com` — welcome emails and SOS |
| `CONTACT_GMAIL_APP_PASSWORD` | Gmail app password for CONTACT_GMAIL_USER — regenerated June 10 |
| `ADMIN_RESET_TOKEN` | Shared secret for `/auth/admin-reset` — regenerate before next use |
| `R2_ACCOUNT_ID` | Cloudflare R2 |
| `R2_ACCESS_KEY_ID` | Cloudflare R2 |
| `R2_SECRET_ACCESS_KEY` | Cloudflare R2 |
| `R2_BUCKET_NAME` | `efr-travel-docs` |
| `R2_ENDPOINT` | R2 S3-compatible endpoint |
| `SECURE_INTAKE_SECRET` | Shared secret for `/secure-intake` webhook |
| `APP_BASE_URL` | `https://bali.escapefromrealitytravel.com` |

---

## Key Endpoints

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/auth/signup` | None | `{email, password, name}` returns `{token, user}` |
| POST | `/auth/signin` | None | `{email, password}` returns `{token, user}` |
| POST | `/auth/change-password` | JWT | `{current_password, new_password}` |
| POST | `/auth/admin-reset` | X-Admin-Token header | `{email, new_password}` — Monet only, no frontend |
| GET | `/documents` | JWT | Trip docs (visible_to_all) + caller's personal docs |
| POST | `/documents/personal` | JWT | Multipart upload to R2 |
| POST | `/documents/trip` | JWT admin | Multipart upload to R2 |
| GET | `/documents/{id}/download` | JWT | Returns 1-hour presigned R2 URL |
| GET | `/messages/group` | JWT | All group messages, ASC |
| POST | `/messages/group` | JWT | Send group message |
| POST | `/sos` | JWT | Fires n8n webhook + Gmail SMTP to `9124328189@vtext.com` |
| POST | `/secure-intake` | Secret | n8n inbound webhook |
| GET | `/health` | None | `{status, database}` |

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

Add new origins here and redeploy the backend whenever a new frontend URL is introduced.

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

# Both sequential
cd backend && flyctl deploy && cd ../frontend && flyctl deploy
```

Frontend Dockerfile does a full `npm ci && npm run build` inside Docker. No local build needed before deploy. `.dockerignore` excludes `node_modules` and `.git`.

---

## Local Dev

```bash
# Backend
cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000

# Frontend
cd frontend && npm run dev   # http://localhost:5173
```

Frontend `.env` points `VITE_API_URL` at the live Fly backend. For local backend testing change it to `http://localhost:8000`.

---

## Admin Password Reset (curl)

```bash
curl -X POST https://backend-little-leaf-7896.fly.dev/auth/admin-reset \
  -H "Content-Type: application/json" \
  -H "X-Admin-Token: <ADMIN_RESET_TOKEN>" \
  -d '{"email": "traveler@example.com", "new_password": "NewPassword123"}'
```

---

## SOS Flow

1. Traveler taps SOS in app and confirms the dialog
2. App calls `POST /sos` with `{level: "HIGH"}`
3. Backend fires n8n webhook (async, non-blocking)
4. Backend sends Gmail SMTP email to `9124328189@vtext.com` (Verizon SMS gateway)
5. Email failure is swallowed so SOS response is never blocked

---

## Database Schema (migrate.py)

Run `python migrate.py` from `backend/` to apply. Safe to re-run (all `CREATE TABLE IF NOT EXISTS` + `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`).

Tables: `travelers`, `channels`, `channel_members`, `messages`, `private_threads`, `private_messages`, `documents`, `triage_log`, `intake_events`, `notifications`.

---

## Three Terminal Workflow (June 10, 2026)

Work was split across three parallel Claude Code terminals:

- **Terminal 1**: Backend work including auth fixes, database migration, admin-reset endpoint, SOS fixes, traveler password resets, git commits, and deploys
- **Terminal 2**: Frontend work including favicon, tab title, document type fixes, and database corrections
- **Terminal 3**: Deep investigation including diagnosing login failures, DB queries, and planning forgot-password flow

All three terminals shared the same Neon database and Fly.io deployment target. Missy coordinated flow, Daniel reviewed security before each commit, Martin and Lilly executed builds.

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

## Open Items (before June 24 launch)

- Test all 9 traveler logins with Pam's group on live webinar
- Regenerate `ADMIN_RESET_TOKEN` (was visible in chat June 10) and update Fly secret
- Twilio parked until budget allows. SOS uses vtext gateway for now.
- Firebase auth migration scheduled post June 15. See auth section for touch points.
