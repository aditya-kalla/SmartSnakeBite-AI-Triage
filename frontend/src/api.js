const BASE = import.meta.env.VITE_API_URL ? `${import.meta.env.VITE_API_URL.replace(/\/$/, '')}/api` : "/api";

export async function transcribeAudio(blob, language) {
  const form = new FormData();
  form.append("audio", blob, "recording.wav");
  form.append("language", language);

  const res = await fetch(`${BASE}/transcribe`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error(`Transcribe failed: ${res.status}`);
  return res.json();
}

export async function runFullPipeline(payload) {
  const res = await fetch(`${BASE}/full-pipeline`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Pipeline failed: ${res.status}`);
  return res.json();
}

export async function speakText(text, language, signal) {
  const res = await fetch(`${BASE}/speak`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, language }),
    signal,
  });
  if (!res.ok) throw new Error(`Speak failed: ${res.status}`);
  return res.blob();
}

export async function speakSummary(severity_class, antivenom_required, language, signal) {
  const res = await fetch(`${BASE}/speak-summary`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ severity_class, antivenom_required, language }),
    signal,
  });
  if (!res.ok) throw new Error(`Speak summary failed: ${res.status}`);
  return res.blob();
}

export async function identifySnakeByPhoto(file) {
  const form = new FormData();
  form.append("image", file);
  const res = await fetch(`${BASE}/snake-id/photo`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Photo identification failed: ${res.status}`);
  }
  return res.json();
}

export async function identifySnakeByDescription(text) {
  const res = await fetch(`${BASE}/snake-id/describe`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Description identification failed: ${res.status}`);
  }
  return res.json();
}

export async function getCases() {
  const res = await fetch(`${BASE}/cases`);
  if (!res.ok) throw new Error(`Failed to fetch cases: ${res.status}`);
  return res.json();
}

export async function getCase(id) {
  const res = await fetch(`${BASE}/cases/${id}`);
  if (!res.ok) throw new Error(`Failed to fetch case: ${res.status}`);
  return res.json();
}

export async function createCase(data) {
  const res = await fetch(`${BASE}/cases`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Failed to create case: ${res.status}`);
  return res.json();
}

export async function updateCase(id, data) {
  const res = await fetch(`${BASE}/cases/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`Failed to update case: ${res.status}`);
  return res.json();
}
