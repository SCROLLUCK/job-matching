const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8888";

export interface Job {
  id: number;
  external_id: string;
  title: string;
  company: string;
  description: string;
  url: string;
  location: string;
  work_mode: "remote" | "hybrid" | "onsite" | "unknown";
  contract_type: "pj" | "clt" | "both" | "unknown";
  salary_min: number | null;
  salary_max: number | null;
  tech_stack: string[];
  experience_level: "junior" | "mid" | "senior" | "unknown";
  source: "linkedin" | "nerdin" | "geekhunter";
  posted_at: string | null;
  scraped_at: string;
  score: number | null;
  application_status: "" | "applied" | "rejected";
  score_breakdown: {
    stack_match?: number;
    salary_match?: number;
    role_match?: number;
    work_mode_match?: number;
    contract_match?: number;
  };
}

export interface UserProfile {
  id: number;
  competencies: string;
  tech_stack: string[];
  desired_salary_min: number | null;
  desired_salary_max: number | null;
  preferred_contract_type: string[];
  preferred_work_mode: string[];
  preferred_roles: string[];
  updated_at: string;
}

export interface JobFilters {
  source?: string;
  contract_type?: string;
  work_mode?: string;
  experience_level?: string;
  min_score?: number;
  salary_min?: number;
  salary_max?: number;
  search?: string;
  sort?: "score" | "date" | "salary" | "scraped";
  application_status?: string;
}

export async function fetchJobs(filters: JobFilters = {}): Promise<Job[]> {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([k, v]) => {
    if (v !== undefined && v !== "" && v !== null) params.set(k, String(v));
  });
  const res = await fetch(`${BASE}/api/jobs/?${params}`);
  return res.json();
}

export async function fetchProfile(): Promise<UserProfile> {
  const res = await fetch(`${BASE}/api/profile/`);
  return res.json();
}

export async function saveProfile(
  data: Partial<UserProfile>,
): Promise<UserProfile> {
  const res = await fetch(`${BASE}/api/profile/`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

async function readSSE(res: Response, onEvent: (data: Record<string, unknown>) => void) {
  const reader = res.body!.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    const parts = buf.split("\n\n");
    buf = parts.pop() ?? "";
    for (const part of parts) {
      const line = part.trim();
      if (line.startsWith("data: ")) {
        try { onEvent(JSON.parse(line.slice(6))); } catch { /* ignore */ }
      }
    }
  }
}

export async function runScrape(
  onEvent: (data: Record<string, unknown>) => void,
  sources?: string[],
): Promise<void> {
  const res = await fetch(`${BASE}/api/scraper/run/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(sources ? { sources } : {}),
  });
  await readSSE(res, onEvent);
}

export async function rescoreJobs(
  onEvent: (data: Record<string, unknown>) => void,
): Promise<void> {
  const res = await fetch(`${BASE}/api/scraper/rescore/`, { method: "POST" });
  await readSSE(res, onEvent);
}

export interface JobStats {
  by_level: { level: string; count: number; avg_salary: number | null }[];
  by_stack: { tech: string; count: number; avg_salary: number | null }[];
}

export async function fetchStats(levels?: string[]): Promise<JobStats> {
  const url =
    levels && levels.length > 0
      ? `${BASE}/api/jobs/stats/?level=${levels.join(",")}`
      : `${BASE}/api/jobs/stats/`;
  const res = await fetch(url);
  return res.json();
}

export async function setJobStatus(
  id: number,
  status: "" | "applied" | "rejected",
): Promise<{ application_status: string }> {
  const res = await fetch(`${BASE}/api/jobs/${id}/status/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
  return res.json();
}
