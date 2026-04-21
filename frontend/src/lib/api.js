const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

export async function fetchJson(path, options) {
  const response = await fetch(`${API_BASE}${path}`, options);
  const payload = await response.json();
  if (!response.ok) {
    const error = new Error(payload.message || `request failed: ${response.status}`);
    error.payload = payload;
    throw error;
  }
  return payload;
}
