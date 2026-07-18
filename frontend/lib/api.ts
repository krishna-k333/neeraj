export const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetcher(path: string) {
  const r = await fetch(`${API_BASE}${path}`);
  if (!r.ok) throw new Error(`API error ${r.status}`);
  return r.json();
}

export const api = {
  get: (path: string) => fetcher(path),
  post: (path: string, body: unknown) =>
    fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then((r) => r.json()),
  patch: (path: string, body: unknown) =>
    fetch(`${API_BASE}${path}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then(async (r) => {
      if (!r.ok) throw new Error(`API error ${r.status}`);
      return r.json();
    }),
  delete: (path: string) => fetch(`${API_BASE}${path}`, { method: "DELETE" }).then((r) => {
    if (!r.ok) throw new Error(`API error ${r.status}`);
    return r.json();
  }),
};
