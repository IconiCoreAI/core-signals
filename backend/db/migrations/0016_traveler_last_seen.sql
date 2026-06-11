-- ITS Integrations: last_seen on travelers, stamped by /auth/signin and
-- /me, surfaced in GET /admin/travelers for the ITS roster view.
-- Numbering continues the ITS migration sequence per Monet (0016).
-- Applied with: venv/bin/python -c "see db/migrations/apply note" or any
-- SQL client; auth.create_table() also adds the column on startup, so a
-- fresh deploy self-heals without this file.

ALTER TABLE travelers ADD COLUMN IF NOT EXISTS last_seen TIMESTAMP;
