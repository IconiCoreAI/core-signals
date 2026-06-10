const API_URL = import.meta.env.VITE_API_URL;

export function getToken() {
  return localStorage.getItem('cs_token');
}

export function getStoredUser() {
  const raw = localStorage.getItem('cs_user');
  return raw ? JSON.parse(raw) : null;
}

export function saveSession(token, user) {
  localStorage.setItem('cs_token', token);
  localStorage.setItem('cs_user', JSON.stringify(user));
}

export function clearSession() {
  localStorage.removeItem('cs_token');
  localStorage.removeItem('cs_user');
}

export async function apiFetch(path, options = {}) {
  const token = getToken();
  const isFormData = options.body instanceof FormData;
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      ...(options.headers || {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(!isFormData && options.body ? { 'Content-Type': 'application/json' } : {}),
    },
  });
  if (res.status === 401) {
    if (!path.startsWith('/auth/')) {
      clearSession();
      window.location.reload();
      return;
    }
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Invalid email or password');
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `API error ${res.status}`);
  }
  return res.json();
}
