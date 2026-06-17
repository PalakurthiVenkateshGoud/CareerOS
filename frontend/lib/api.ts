const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function uploadResume(file: File) {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${BASE}/api/resume/upload`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to upload resume");
  }

  return res.json();
}

export async function configureCareer(
  sessionId: string,
  targetRole: string,
  hoursPerWeek: number
) {
  const res = await fetch(`${BASE}/api/career/configure`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      target_role: targetRole,
      hours_per_week: hoursPerWeek,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to save configuration");
  }

  return res.json();
}

export async function analyzeCareer(
  sessionId: string,
  targetRole: string,
  hoursPerWeek: number
) {
  const res = await fetch(`${BASE}/api/career/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      target_role: targetRole,
      hours_per_week: hoursPerWeek,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to analyze career data");
  }

  return res.json();
}

export async function getDashboard(sessionId: string) {
  const res = await fetch(`${BASE}/api/career/dashboard/${sessionId}`);

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to fetch dashboard");
  }

  return res.json();
}