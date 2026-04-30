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
  score_breakdown: {
    stack_match?: number;
    salary_match?: number;
    role_match?: number;
    work_mode_match?: number;
    contract_match?: number;
    summary?: string;
  };
}

export interface UserProfile {
  id: number;
  competencies: string;
  tech_stack: string[];
  desired_salary_min: number | null;
  desired_salary_max: number | null;
  preferred_contract_type: "pj" | "clt" | "both";
  preferred_work_mode: "remote" | "hybrid" | "onsite" | "any";
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

export async function saveProfile(data: Partial<UserProfile>): Promise<UserProfile> {
  const res = await fetch(`${BASE}/api/profile/`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function runScrape(sources?: string[]): Promise<Record<string, unknown>> {
  const res = await fetch(`${BASE}/api/scraper/run/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(sources ? { sources } : {}),
  });
  return res.json();
}

export async function rescoreJobs(): Promise<{ updated: number }> {
  const res = await fetch(`${BASE}/api/scraper/rescore/`, { method: "POST" });
  return res.json();
}
