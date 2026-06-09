import supabase from './supabaseClient';

const API_URL = import.meta.env.VITE_API_URL;

async function getToken() {
  const { data } = await supabase.auth.getSession();
  return data.session?.access_token;
}

export async function apiFetch(path, options = {}) {
  const token = await getToken();
  const isFormData = options.body instanceof FormData;
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      ...(options.headers || {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(!isFormData && options.body ? { 'Content-Type': 'application/json' } : {}),
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `API error ${res.status}`);
  }
  return res.json();
}
