import { useState, useEffect, useRef } from "react";
import { apiFetch, saveSession, clearSession, getStoredUser, getToken } from "./api";

const COLORS = {
  teal: "#1C9598",
  purple: "#69508A",
  caramel: "#B37D5B",
  lightTeal: "#B0E2DF",
  lightPurple: "#B1A1ED",
  red: "#D32F2F",
  white: "#FFFFFF",
  black: "#000000",
  bubbleGray: "#F0F0F0",
  textGray: "#555555",
  borderGray: "#DDDDDD",
};

const TRIP = {
  name: "Bali Retirement Trip",
  destination: "Bali, Indonesia",
  dates: "June 23 – July 3, 2026",
  travelers: 10,
};

const QUICK_ACCESS = [
  { label: "Group chat", icon: "💬", color: COLORS.teal },
  { label: "Itinerary", icon: "📅", color: COLORS.purple },
  { label: "Hotel & transfers", icon: "🏨", color: COLORS.caramel },
  { label: "Emergency help", icon: "🚨", color: COLORS.red },
];

const TABS = [
  { id: "home", label: "Home", icon: "🏠" },
  { id: "group", label: "Group", icon: "👥" },
  { id: "docs", label: "Docs", icon: "📄" },
  { id: "help", label: "Help", icon: "🆘" },
];

const s = {
  app: {
    fontFamily: "'Segoe UI', system-ui, sans-serif",
    maxWidth: 480,
    margin: "0 auto",
    minHeight: "100dvh",
    display: "flex",
    flexDirection: "column",
    backgroundColor: COLORS.white,
    position: "relative",
  },
  header: {
    backgroundColor: COLORS.teal,
    padding: "16px 20px 12px",
    position: "sticky",
    top: 0,
    zIndex: 10,
  },
  headerTitle: {
    color: COLORS.white,
    fontSize: 18,
    fontWeight: 700,
    margin: 0,
  },
  headerDates: {
    color: COLORS.white,
    fontSize: 13,
    opacity: 0.9,
    marginTop: 2,
  },
  tagline: {
    backgroundColor: COLORS.lightTeal,
    textAlign: "center",
    padding: "8px 16px",
    fontSize: 12,
    fontStyle: "italic",
    color: COLORS.black,
    letterSpacing: "0.02em",
  },
  scrollArea: {
    flex: 1,
    overflowY: "auto",
    paddingBottom: 72,
  },
  bottomBar: {
    position: "fixed",
    bottom: 0,
    left: "50%",
    transform: "translateX(-50%)",
    width: "100%",
    maxWidth: 480,
    backgroundColor: COLORS.lightTeal,
    display: "flex",
    borderTop: `1px solid ${COLORS.borderGray}`,
    zIndex: 20,
  },
  tabBtn: (active) => ({
    flex: 1,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    padding: "10px 0 8px",
    background: "none",
    border: "none",
    borderBottom: active ? `3px solid ${COLORS.purple}` : "3px solid transparent",
    color: active ? COLORS.purple : COLORS.teal,
    fontSize: 10,
    fontWeight: active ? 700 : 400,
    cursor: "pointer",
    gap: 2,
  }),
  tabIcon: {
    fontSize: 20,
  },
  tripCard: {
    margin: 16,
    borderRadius: 14,
    backgroundColor: COLORS.purple,
    padding: 20,
    color: COLORS.white,
    boxShadow: "0 4px 12px rgba(105,80,138,0.25)",
  },
  tripCardName: {
    fontSize: 20,
    fontWeight: 700,
    margin: "0 0 4px",
  },
  tripCardDest: {
    fontSize: 14,
    opacity: 0.85,
    margin: "0 0 12px",
  },
  tripMeta: {
    display: "flex",
    gap: 16,
    fontSize: 13,
  },
  tripMetaItem: {
    display: "flex",
    alignItems: "center",
    gap: 4,
    opacity: 0.9,
  },
  sectionLabel: {
    fontSize: 13,
    fontWeight: 600,
    color: COLORS.textGray,
    textTransform: "uppercase",
    letterSpacing: "0.06em",
    padding: "0 16px",
    marginBottom: 8,
    marginTop: 4,
  },
  quickList: {
    margin: "0 16px",
    borderRadius: 12,
    overflow: "hidden",
    border: `1px solid ${COLORS.borderGray}`,
  },
  quickItem: {
    display: "flex",
    alignItems: "center",
    padding: "14px 16px",
    backgroundColor: COLORS.white,
    borderBottom: `1px solid ${COLORS.borderGray}`,
    cursor: "pointer",
    gap: 14,
  },
  quickItemLast: {
    borderBottom: "none",
  },
  iconCircle: (color) => ({
    width: 40,
    height: 40,
    borderRadius: "50%",
    backgroundColor: color,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: 18,
    flexShrink: 0,
  }),
  quickLabel: {
    flex: 1,
    fontSize: 15,
    color: COLORS.black,
  },
  chevron: {
    color: COLORS.textGray,
    fontSize: 16,
  },
  chatArea: {
    display: "flex",
    flexDirection: "column",
    gap: 10,
    padding: "16px 16px 0",
  },
  bubble: (mine) => ({
    maxWidth: "72%",
    alignSelf: mine ? "flex-end" : "flex-start",
    backgroundColor: mine ? COLORS.purple : COLORS.teal,
    color: COLORS.white,
    borderRadius: mine ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
    padding: "10px 14px",
  }),
  bubbleSender: {
    fontSize: 11,
    fontWeight: 600,
    opacity: 0.75,
    marginBottom: 3,
  },
  bubbleText: {
    fontSize: 15,
    lineHeight: 1.4,
  },
  chatInputRow: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    padding: "12px 16px",
    borderTop: `1px solid ${COLORS.borderGray}`,
    backgroundColor: COLORS.white,
    position: "sticky",
    bottom: 72,
  },
  chatInput: {
    flex: 1,
    border: `1px solid ${COLORS.borderGray}`,
    borderRadius: 24,
    padding: "10px 16px",
    fontSize: 15,
    outline: "none",
    backgroundColor: COLORS.bubbleGray,
  },
  sendBtn: {
    backgroundColor: COLORS.teal,
    color: COLORS.white,
    border: "none",
    borderRadius: "50%",
    width: 40,
    height: 40,
    fontSize: 18,
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
  },
  docSection: {
    margin: "16px 16px 0",
  },
  docSectionTitle: {
    fontSize: 15,
    fontWeight: 700,
    color: COLORS.black,
    marginBottom: 10,
  },
  docList: {
    borderRadius: 12,
    overflow: "hidden",
    border: `1px solid ${COLORS.borderGray}`,
    marginBottom: 20,
  },
  docItem: {
    display: "flex",
    alignItems: "center",
    padding: "14px 16px",
    backgroundColor: COLORS.white,
    borderBottom: `1px solid ${COLORS.borderGray}`,
    gap: 12,
  },
  docItemLast: {
    borderBottom: "none",
  },
  docIcon: {
    fontSize: 22,
    flexShrink: 0,
  },
  docMeta: {
    flex: 1,
  },
  docName: {
    fontSize: 14,
    fontWeight: 600,
    color: COLORS.black,
  },
  docSize: {
    fontSize: 12,
    color: COLORS.textGray,
    marginTop: 2,
  },
  downloadBtn: {
    backgroundColor: "transparent",
    border: `1px solid ${COLORS.teal}`,
    color: COLORS.teal,
    borderRadius: 8,
    padding: "5px 10px",
    fontSize: 12,
    cursor: "pointer",
    fontWeight: 600,
  },
  uploadBtn: {
    backgroundColor: COLORS.caramel,
    color: COLORS.white,
    border: "none",
    borderRadius: 10,
    padding: "12px 20px",
    fontSize: 15,
    fontWeight: 600,
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    gap: 8,
  },
  helpScreen: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    padding: "60px 24px",
    gap: 20,
    textAlign: "center",
  },
  sosBtn: {
    width: 160,
    height: 160,
    borderRadius: "50%",
    backgroundColor: COLORS.red,
    color: COLORS.white,
    border: "none",
    fontSize: 22,
    fontWeight: 900,
    cursor: "pointer",
    boxShadow: "0 0 0 12px rgba(211,47,47,0.15), 0 6px 24px rgba(211,47,47,0.4)",
    letterSpacing: "0.05em",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    gap: 4,
  },
  sosSubLabel: {
    fontSize: 12,
    opacity: 0.85,
    fontWeight: 400,
  },
  helpNote: {
    fontSize: 14,
    color: COLORS.textGray,
    maxWidth: 280,
    lineHeight: 1.6,
  },
  // Auth screen
  authWrap: {
    minHeight: "100dvh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: COLORS.white,
    padding: 24,
  },
  authCard: {
    width: "100%",
    maxWidth: 360,
    display: "flex",
    flexDirection: "column",
    gap: 16,
  },
  authLogo: {
    textAlign: "center",
    fontSize: 28,
    fontWeight: 800,
    color: COLORS.teal,
    letterSpacing: "-0.02em",
    marginBottom: 4,
  },
  authSub: {
    textAlign: "center",
    fontSize: 13,
    color: COLORS.textGray,
    marginTop: -8,
    marginBottom: 8,
  },
  authInput: {
    width: "100%",
    boxSizing: "border-box",
    border: `1px solid ${COLORS.borderGray}`,
    borderRadius: 10,
    padding: "12px 14px",
    fontSize: 15,
    outline: "none",
    backgroundColor: COLORS.bubbleGray,
  },
  authBtn: {
    width: "100%",
    backgroundColor: COLORS.teal,
    color: COLORS.white,
    border: "none",
    borderRadius: 10,
    padding: "13px",
    fontSize: 15,
    fontWeight: 600,
    cursor: "pointer",
  },
  authToggle: {
    background: "none",
    border: "none",
    color: COLORS.purple,
    fontSize: 13,
    cursor: "pointer",
    textDecoration: "underline",
    padding: 0,
    textAlign: "center",
  },
  authError: {
    fontSize: 13,
    color: COLORS.red,
    textAlign: "center",
    padding: "8px 12px",
    backgroundColor: "#fdecea",
    borderRadius: 8,
  },
  emptyState: {
    fontSize: 13,
    color: COLORS.textGray,
    textAlign: "center",
    padding: "32px 16px",
    fontStyle: "italic",
  },
};

// ─── Auth Screen ────────────────────────────────────────────────────────────

function AuthScreen({ onAuth }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [mode, setMode] = useState("signin");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const endpoint = mode === "signup" ? "/auth/signup" : "/auth/signin";
      const body = mode === "signup"
        ? { email, password, name }
        : { email, password };
      const data = await apiFetch(endpoint, {
        method: "POST",
        body: JSON.stringify(body),
      });
      saveSession(data.token, data.user);
      onAuth(data.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={s.authWrap}>
      <div style={s.authCard}>
        <p style={s.authLogo}>Core Signals</p>
        <p style={s.authSub}>where bucket list dreams come true</p>
        <form onSubmit={submit} style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {mode === "signup" && (
            <input
              style={s.authInput}
              type="text"
              placeholder="Your name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoComplete="name"
            />
          )}
          <input
            style={s.authInput}
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
          />
          <input
            style={s.authInput}
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete={mode === "signup" ? "new-password" : "current-password"}
          />
          {error && <p style={s.authError}>{error}</p>}
          <button style={s.authBtn} type="submit" disabled={loading}>
            {loading ? "…" : mode === "signin" ? "Sign in" : "Create account"}
          </button>
        </form>
        <button
          style={s.authToggle}
          onClick={() => { setMode(mode === "signin" ? "signup" : "signin"); setError(null); }}
        >
          {mode === "signin" ? "No account? Sign up" : "Have an account? Sign in"}
        </button>
      </div>
    </div>
  );
}

// ─── Change Name Modal ───────────────────────────────────────────────────────

function ChangeNameModal({ session, onClose, onSave }) {
  const [name, setName] = useState(session?.name || "");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  const overlay = {
    position: "fixed", inset: 0, backgroundColor: "rgba(0,0,0,0.5)",
    display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100, padding: 24,
  };
  const card = {
    backgroundColor: COLORS.white, borderRadius: 16, padding: 28,
    width: "100%", maxWidth: 340, display: "flex", flexDirection: "column", gap: 12,
  };

  async function submit(e) {
    e.preventDefault();
    setError(null);
    const trimmed = name.trim();
    if (!trimmed) { setError("Name cannot be empty"); return; }
    setLoading(true);
    try {
      const updated = await apiFetch("/auth/update-name", {
        method: "PATCH",
        body: JSON.stringify({ name: trimmed }),
      });
      saveSession(getToken(), updated);
      onSave(updated);
      setDone(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (done) return (
    <div style={overlay} onClick={onClose}>
      <div style={card} onClick={e => e.stopPropagation()}>
        <p style={{ fontSize: 16, fontWeight: 700, color: COLORS.teal, textAlign: "center" }}>Name updated ✓</p>
        <button style={s.authBtn} onClick={onClose}>Done</button>
      </div>
    </div>
  );

  return (
    <div style={overlay} onClick={onClose}>
      <div style={card} onClick={e => e.stopPropagation()}>
        <p style={{ fontSize: 16, fontWeight: 700, color: COLORS.black, margin: 0 }}>Change display name</p>
        <form onSubmit={submit} style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          <input style={s.authInput} type="text" placeholder="Your name" value={name}
            onChange={e => setName(e.target.value)} required autoComplete="name" />
          {error && <p style={s.authError}>{error}</p>}
          <button style={s.authBtn} type="submit" disabled={loading}>
            {loading ? "Saving…" : "Save name"}
          </button>
        </form>
        <button style={s.authToggle} onClick={onClose}>Cancel</button>
      </div>
    </div>
  );
}

// ─── Change Password Modal ───────────────────────────────────────────────────

function ChangePasswordModal({ onClose }) {
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setError(null);
    if (next !== confirm) { setError("New passwords don't match"); return; }
    if (next.length < 8) { setError("New password must be at least 8 characters"); return; }
    setLoading(true);
    try {
      await apiFetch("/auth/change-password", {
        method: "POST",
        body: JSON.stringify({ current_password: current, new_password: next }),
      });
      setDone(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const overlay = {
    position: "fixed", inset: 0, backgroundColor: "rgba(0,0,0,0.5)",
    display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100,
    padding: 24,
  };
  const card = {
    backgroundColor: COLORS.white, borderRadius: 16, padding: 28,
    width: "100%", maxWidth: 340, display: "flex", flexDirection: "column", gap: 12,
  };

  if (done) return (
    <div style={overlay} onClick={onClose}>
      <div style={card} onClick={e => e.stopPropagation()}>
        <p style={{ fontSize: 16, fontWeight: 700, color: COLORS.teal, textAlign: "center" }}>Password updated ✓</p>
        <button style={s.authBtn} onClick={onClose}>Done</button>
      </div>
    </div>
  );

  return (
    <div style={overlay} onClick={onClose}>
      <div style={card} onClick={e => e.stopPropagation()}>
        <p style={{ fontSize: 16, fontWeight: 700, color: COLORS.black, margin: 0 }}>Change password</p>
        <form onSubmit={submit} style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          <input style={s.authInput} type="password" placeholder="Current password" value={current}
            onChange={e => setCurrent(e.target.value)} required autoComplete="current-password" />
          <input style={s.authInput} type="password" placeholder="New password" value={next}
            onChange={e => setNext(e.target.value)} required autoComplete="new-password" />
          <input style={s.authInput} type="password" placeholder="Confirm new password" value={confirm}
            onChange={e => setConfirm(e.target.value)} required autoComplete="new-password" />
          {error && <p style={s.authError}>{error}</p>}
          <button style={s.authBtn} type="submit" disabled={loading}>
            {loading ? "Updating…" : "Update password"}
          </button>
        </form>
        <button style={s.authToggle} onClick={onClose}>Cancel</button>
      </div>
    </div>
  );
}

// ─── Header ─────────────────────────────────────────────────────────────────

function Header({ onSignOut, onChangePw, onChangeName }) {
  return (
    <>
      <div style={s.header}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <p style={s.headerTitle}>{TRIP.name}</p>
            <p style={s.headerDates}>{TRIP.destination} · {TRIP.dates}</p>
          </div>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 4 }}>
            <button
              onClick={onSignOut}
              style={{ background: "none", border: "none", color: "rgba(255,255,255,0.7)", fontSize: 12, cursor: "pointer", padding: 0 }}
            >
              Sign out
            </button>
            <button
              onClick={onChangePw}
              style={{ background: "none", border: "none", color: "rgba(255,255,255,0.55)", fontSize: 11, cursor: "pointer", padding: 0 }}
            >
              Change password
            </button>
            <button
              onClick={onChangeName}
              style={{ background: "none", border: "none", color: "rgba(255,255,255,0.55)", fontSize: 11, cursor: "pointer", padding: 0 }}
            >
              Change name
            </button>
          </div>
        </div>
      </div>
      <div style={s.tagline}>where bucket list dreams come true</div>
    </>
  );
}

// ─── Hotel & Transfers Screen ─────────────────────────────────────────────────

function HotelScreen({ onTabChange }) {
  return (
    <div style={{ paddingBottom: 8 }}>
      <div style={{ padding: "12px 16px 0" }}>
        <button
          onClick={() => onTabChange("home")}
          style={{ background: "none", border: "none", color: COLORS.teal, fontSize: 15, cursor: "pointer", padding: 0, fontWeight: 600 }}
        >
          ← Back
        </button>
      </div>

      <div style={{ margin: "12px 16px 0", borderRadius: 14, backgroundColor: COLORS.caramel, padding: 20, color: COLORS.white, boxShadow: "0 4px 12px rgba(179,125,91,0.25)" }}>
        <p style={{ fontSize: 18, fontWeight: 700, margin: "0 0 6px" }}>Taman Dharmawangsa Suites</p>
        <p style={{ fontSize: 13, opacity: 0.9, margin: 0 }}>Two Bedroom Pool Villa · Daily Breakfast Included</p>
      </div>

      <div style={{ margin: "12px 16px 0", borderRadius: 12, border: `1px solid ${COLORS.borderGray}`, overflow: "hidden" }}>
        <div style={{ padding: "14px 16px", borderBottom: `1px solid ${COLORS.borderGray}` }}>
          <p style={{ fontSize: 12, fontWeight: 600, color: COLORS.textGray, textTransform: "uppercase", letterSpacing: "0.06em", margin: "0 0 6px" }}>Address</p>
          <p style={{ fontSize: 14, color: COLORS.black, margin: 0, lineHeight: 1.6 }}>
            Jl. Astina Pura No.1, Jl. Raya Kampial<br />
            Nusa Dua, Benoa, Kecamatan Kuta Selatan<br />
            Badung, Bali, Indonesia 80361
          </p>
        </div>
        <div style={{ padding: "14px 16px" }}>
          <p style={{ fontSize: 12, fontWeight: 600, color: COLORS.textGray, textTransform: "uppercase", letterSpacing: "0.06em", margin: "0 0 6px" }}>Phone &amp; WhatsApp</p>
          <a href="tel:+6281138017999" style={{ fontSize: 14, color: COLORS.caramel, textDecoration: "none", fontWeight: 600 }}>
            +62 81 138 017 999
          </a>
        </div>
      </div>

      <p style={{ ...s.sectionLabel, marginTop: 20 }}>Airport pickups</p>

      <div style={{ margin: "0 16px 12px", borderRadius: 12, border: `1px solid ${COLORS.borderGray}`, overflow: "hidden" }}>
        <div style={{ backgroundColor: COLORS.purple, padding: "10px 16px" }}>
          <p style={{ color: COLORS.white, fontSize: 14, fontWeight: 700, margin: 0 }}>June 23, 2026</p>
        </div>
        <div style={{ padding: "14px 16px" }}>
          <p style={{ fontSize: 12, fontWeight: 600, color: COLORS.textGray, textTransform: "uppercase", letterSpacing: "0.05em", margin: "0 0 6px" }}>Korean Airlines KE633 · ETA 11:50pm</p>
          <p style={{ fontSize: 14, color: COLORS.black, margin: "0 0 6px" }}>Francine Applewhite, Lorine Hall</p>
          <p style={{ fontSize: 12, color: COLORS.textGray, margin: 0 }}>1x MPV Car</p>
        </div>
      </div>

      <div style={{ margin: "0 16px 12px", borderRadius: 12, border: `1px solid ${COLORS.borderGray}`, overflow: "hidden" }}>
        <div style={{ backgroundColor: COLORS.purple, padding: "10px 16px" }}>
          <p style={{ color: COLORS.white, fontSize: 14, fontWeight: 700, margin: 0 }}>June 24, 2026</p>
        </div>
        <div style={{ padding: "14px 16px", borderBottom: `1px solid ${COLORS.borderGray}` }}>
          <p style={{ fontSize: 12, fontWeight: 600, color: COLORS.textGray, textTransform: "uppercase", letterSpacing: "0.05em", margin: "0 0 6px" }}>Cathay Pacific CX783 · ETA 5:40pm</p>
          <p style={{ fontSize: 14, color: COLORS.black, margin: "0 0 6px", lineHeight: 1.5 }}>
            Pamela Washington, Cindy Notti, Veronica Barnes,{" "}
            Carla Kirkland, Lourdes Bernal, Tiana Towns, Judy Jackson
          </p>
          <p style={{ fontSize: 12, color: COLORS.textGray, margin: 0 }}>2x MPV Car</p>
        </div>
        <div style={{ padding: "14px 16px" }}>
          <p style={{ fontSize: 12, fontWeight: 600, color: COLORS.textGray, textTransform: "uppercase", letterSpacing: "0.05em", margin: "0 0 6px" }}>Singapore Airlines SQ938 · ETA 12:00pm</p>
          <p style={{ fontSize: 14, color: COLORS.black, margin: "0 0 6px" }}>Cynthia A. Franklin</p>
          <p style={{ fontSize: 12, color: COLORS.textGray, margin: 0 }}>1x MPV Car</p>
        </div>
      </div>

      <div style={{ margin: "0 16px 20px", borderRadius: 12, backgroundColor: "#FFF8F4", border: `1px solid ${COLORS.caramel}`, padding: "14px 16px" }}>
        <p style={{ fontSize: 13, fontWeight: 700, color: COLORS.caramel, margin: "0 0 4px" }}>Your driver meets you at the arrival gate</p>
        <p style={{ fontSize: 13, color: COLORS.textGray, margin: "0 0 10px" }}>Transfer trouble? WhatsApp the hotel directly:</p>
        <a href="https://wa.me/6281138017999" style={{ fontSize: 15, color: COLORS.caramel, textDecoration: "none", fontWeight: 700 }}>
          +62 81 138 017 999
        </a>
      </div>
    </div>
  );
}

// ─── Home Screen ─────────────────────────────────────────────────────────────

function HomeScreen({ onTabChange }) {
  const quickWithNav = QUICK_ACCESS.map((item) => ({
    ...item,
    tab: item.label === "Group chat" ? "group"
      : item.label === "Emergency help" ? "help"
      : item.label === "Itinerary" ? "docs"
      : item.label === "Hotel & transfers" ? "hotel"
      : null,
  }));

  return (
    <div>
      <div style={s.tripCard}>
        <p style={s.tripCardName}>{TRIP.name}</p>
        <p style={s.tripCardDest}>{TRIP.destination}</p>
        <div style={s.tripMeta}>
          <span style={s.tripMetaItem}>📅 {TRIP.dates}</span>
          <span style={s.tripMetaItem}>👥 {TRIP.travelers} travelers</span>
        </div>
      </div>

      <p style={s.sectionLabel}>Quick access</p>
      <div style={s.quickList}>
        {quickWithNav.map((item, i) => (
          <div
            key={item.label}
            style={{ ...s.quickItem, ...(i === QUICK_ACCESS.length - 1 ? s.quickItemLast : {}) }}
            onClick={() => item.tab && onTabChange(item.tab)}
          >
            <div style={s.iconCircle(item.color)}>{item.icon}</div>
            <span style={s.quickLabel}>{item.label}</span>
            <span style={s.chevron}>›</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Group Screen ────────────────────────────────────────────────────────────

function GroupScreen({ session }) {
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const bottomRef = useRef(null);
  const myId = session?.id;

  useEffect(() => {
    apiFetch("/messages/group")
      .then(setMessages)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send() {
    const text = draft.trim();
    if (!text || sending) return;
    setDraft("");
    setSending(true);
    try {
      const msg = await apiFetch("/messages/group", {
        method: "POST",
        body: JSON.stringify({ body: text }),
      });
      setMessages((prev) => [...prev, msg]);
    } catch (err) {
      console.error(err);
    } finally {
      setSending(false);
    }
  }

  function handleKey(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  function displayName(msg) {
    if (msg.sender_id === myId) return "You";
    return msg.sender_name?.split(" ")[0] || "Unknown";
  }

  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      <div style={s.chatArea}>
        {loading && <p style={s.emptyState}>Loading messages…</p>}
        {!loading && messages.length === 0 && (
          <p style={s.emptyState}>No messages yet. Say hi! 👋</p>
        )}
        {messages.map((msg) => {
          const mine = msg.sender_id === myId;
          return (
            <div key={msg.id} style={s.bubble(mine)}>
              {!mine && <div style={s.bubbleSender}>{displayName(msg)}</div>}
              <div style={s.bubbleText}>{msg.body}</div>
            </div>
          );
        })}
        <div ref={bottomRef} />
      </div>
      <div style={s.chatInputRow}>
        <input
          style={s.chatInput}
          placeholder="Message the group…"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={handleKey}
        />
        <button style={s.sendBtn} onClick={send} aria-label="Send" disabled={sending}>➤</button>
      </div>
    </div>
  );
}

// ─── Docs Screen ─────────────────────────────────────────────────────────────

function DocsScreen({ session }) {
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);
  const myId = session?.id;

  useEffect(() => {
    apiFetch("/documents")
      .then(setDocs)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  async function handleDownload(id) {
    try {
      const { url } = await apiFetch(`/documents/${id}/download`);
      window.open(url, "_blank");
    } catch (e) {
      alert(e.message);
    }
  }

  async function handleUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    const form = new FormData();
    form.append("file", file);
    form.append("document_type", "other");
    try {
      const doc = await apiFetch("/documents/personal", { method: "POST", body: form });
      setDocs((prev) => [doc, ...prev]);
    } catch (e) {
      alert(e.message);
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  const tripDocs = docs.filter((d) => d.visible_to_all);
  const personalDocs = docs.filter((d) => !d.visible_to_all && d.uploaded_by === myId);

  function DocRow({ doc, icon, last }) {
    return (
      <div style={{ ...s.docItem, ...(last ? s.docItemLast : {}) }}>
        <span style={s.docIcon}>{icon}</span>
        <div style={s.docMeta}>
          <div style={s.docName}>{doc.filename}</div>
          <div style={s.docSize}>{doc.document_type}</div>
        </div>
        <button style={s.downloadBtn} onClick={() => handleDownload(doc.id)}>⬇ Open</button>
      </div>
    );
  }

  return (
    <div>
      <div style={s.docSection}>
        <p style={s.docSectionTitle}>Trip documents</p>
        {loading ? (
          <p style={s.emptyState}>Loading…</p>
        ) : tripDocs.length === 0 ? (
          <p style={s.emptyState}>No trip documents yet.</p>
        ) : (
          <div style={s.docList}>
            {tripDocs.map((doc, i) => (
              <DocRow key={doc.id} doc={doc} icon="📋" last={i === tripDocs.length - 1} />
            ))}
          </div>
        )}

        <p style={s.docSectionTitle}>Personal documents</p>
        {!loading && personalDocs.length === 0 ? (
          <p style={s.emptyState}>No personal documents uploaded yet.</p>
        ) : (
          <div style={s.docList}>
            {personalDocs.map((doc, i) => (
              <DocRow key={doc.id} doc={doc} icon="🪪" last={i === personalDocs.length - 1} />
            ))}
          </div>
        )}

        <input
          ref={fileInputRef}
          type="file"
          style={{ display: "none" }}
          onChange={handleUpload}
          accept=".pdf,.jpg,.jpeg,.png"
        />
        <button
          style={s.uploadBtn}
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
        >
          <span>⬆</span> {uploading ? "Uploading…" : "Upload document"}
        </button>
      </div>
    </div>
  );
}

// ─── Help Screen ─────────────────────────────────────────────────────────────

function HelpScreen() {
  const [sent, setSent] = useState(false);
  const [sending, setSending] = useState(false);

  async function handleSOS() {
    if (sending || sent) return;
    if (!window.confirm("Send emergency SOS? Your travel agent will be alerted immediately.")) return;
    setSending(true);
    try {
      await apiFetch("/sos", { method: "POST", body: JSON.stringify({ level: "HIGH" }) });
      setSent(true);
    } catch {
      alert("Could not send SOS signal. Please call emergency services directly.");
    } finally {
      setSending(false);
    }
  }

  return (
    <div style={s.helpScreen}>
      <button
        style={{
          ...s.sosBtn,
          ...(sent ? { backgroundColor: "#388e3c", boxShadow: "0 0 0 12px rgba(56,142,60,0.15), 0 6px 24px rgba(56,142,60,0.4)" } : {}),
          opacity: sending ? 0.7 : 1,
        }}
        aria-label="Emergency SOS"
        onClick={handleSOS}
        disabled={sending}
      >
        <span>{sent ? "✓ SENT" : "SOS"}</span>
        <span style={s.sosSubLabel}>{sent ? "Help is coming" : "Emergency"}</span>
      </button>
      <p style={s.helpNote}>
        {sent
          ? "Your SOS has been sent. Your travel agent has been alerted and help is on the way."
          : "Press SOS to immediately alert your travel agent. For life-threatening emergencies, call local emergency services directly."}
      </p>
    </div>
  );
}

// ─── App ─────────────────────────────────────────────────────────────────────

const SCREENS = { home: HomeScreen, group: GroupScreen, docs: DocsScreen, help: HelpScreen, hotel: HotelScreen };

export default function App() {
  const [session, setSession] = useState(() => {
    const user = getStoredUser();
    const token = getToken();
    return user && token ? user : null;
  });
  const [activeTab, setActiveTab] = useState("home");
  const [showChangePw, setShowChangePw] = useState(false);
  const [showChangeName, setShowChangeName] = useState(false);

  function signOut() {
    clearSession();
    setSession(null);
  }

  if (!session) {
    return <AuthScreen onAuth={setSession} />;
  }

  const Screen = SCREENS[activeTab];
  const screenProps = { session };

  return (
    <div style={s.app}>
      {showChangePw && <ChangePasswordModal onClose={() => setShowChangePw(false)} />}
      {showChangeName && (
        <ChangeNameModal
          session={session}
          onClose={() => setShowChangeName(false)}
          onSave={(updated) => { setSession(updated); setShowChangeName(false); }}
        />
      )}
      <Header onSignOut={signOut} onChangePw={() => setShowChangePw(true)} onChangeName={() => setShowChangeName(true)} />
      <div style={s.scrollArea}>
        <Screen {...screenProps} onTabChange={setActiveTab} />
      </div>
      <nav style={s.bottomBar} role="navigation" aria-label="Main tabs">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            style={s.tabBtn(activeTab === tab.id)}
            onClick={() => setActiveTab(tab.id)}
            aria-current={activeTab === tab.id ? "page" : undefined}
          >
            <span style={s.tabIcon}>{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </nav>
    </div>
  );
}
