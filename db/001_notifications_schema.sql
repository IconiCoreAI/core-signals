CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    type VARCHAR(50) NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    metadata JSONB,
    read BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Recommended indices for fast querying and filtering
CREATE INDEX IF NOT EXISTS idx_notifications_source ON notifications(source);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC);
