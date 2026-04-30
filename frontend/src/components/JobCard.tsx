import { Job } from "../api";
import ScoreBar from "./ScoreBar";

const SOURCE_LABELS: Record<string, string> = {
  linkedin: "LinkedIn",
  nerdin: "Nerdin",
  geekhunter: "GeekhHunter",
};

const SOURCE_COLORS: Record<string, string> = {
  linkedin: "bg-blue-100 text-blue-700",
  nerdin: "bg-purple-100 text-purple-700",
  geekhunter: "bg-green-100 text-green-700",
};

function salaryLabel(min: number | null, max: number | null): string {
  if (!min && !max) return "";
  const fmt = (n: number) => `R$${(n / 1000).toFixed(0)}k`;
  if (min && max) return `${fmt(min)} – ${fmt(max)}`;
  if (max) return `up to ${fmt(max)}`;
  return `from ${fmt(min!)}`;
}

export default function JobCard({ job }: { job: Job }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5 flex flex-col gap-3 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <a href={job.url} target="_blank" rel="noopener noreferrer" className="font-semibold text-gray-900 hover:text-blue-600 line-clamp-2">
            {job.title}
          </a>
          {job.company && <p className="text-sm text-gray-500 mt-0.5">{job.company}</p>}
        </div>
        <span className={`shrink-0 text-xs font-medium px-2 py-0.5 rounded-full ${SOURCE_COLORS[job.source]}`}>
          {SOURCE_LABELS[job.source]}
        </span>
      </div>

      <div className="flex flex-wrap gap-2 text-xs text-gray-600">
        {job.location && <span>📍 {job.location}</span>}
        {job.work_mode !== "unknown" && <span className="capitalize">🏠 {job.work_mode}</span>}
        {job.contract_type !== "unknown" && <span className="uppercase">📄 {job.contract_type}</span>}
        {job.experience_level !== "unknown" && <span className="capitalize">⭐ {job.experience_level}</span>}
        {salaryLabel(job.salary_min, job.salary_max) && <span>💰 {salaryLabel(job.salary_min, job.salary_max)}</span>}
      </div>

      {job.tech_stack.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {job.tech_stack.slice(0, 8).map((tag) => (
            <span key={tag} className="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">{tag}</span>
          ))}
          {job.tech_stack.length > 8 && <span className="text-xs text-gray-400">+{job.tech_stack.length - 8}</span>}
        </div>
      )}

      <ScoreBar score={job.score} breakdown={job.score_breakdown} />
    </div>
  );
}
